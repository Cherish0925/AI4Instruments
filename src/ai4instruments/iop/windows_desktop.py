"""WebView2 window using public Windows Forms APIs on CoreCLR."""
from __future__ import annotations
import json
import os
import sysconfig
import threading
import webbrowser
from pathlib import Path
from types import SimpleNamespace


def open_window(url, storage, open_browser, on_loaded=None):
    import clr
    from webview.util import interop_dll_path
    loader = interop_dll_path('win-arm64' if sysconfig.get_platform() == 'win-arm64' else 'win-x64')
    dll_directory = os.add_dll_directory(loader)
    clr.AddReference(interop_dll_path('Microsoft.Web.WebView2.Core.dll'))
    clr.AddReference(interop_dll_path('Microsoft.Web.WebView2.WinForms.dll'))
    from Microsoft.Web.WebView2.WinForms import WebView2, CoreWebView2CreationProperties
    from System import Action
    from System.Drawing import Icon, Size
    from System.Threading import ApartmentState, Thread, ThreadStart
    from System.Windows.Forms import Application, AutoScaleMode, DockStyle, Form, FormStartPosition

    storage = Path(storage)
    storage.mkdir(parents=True, exist_ok=True)
    errors = []

    class Window:
        def __init__(self, form, control):
            self.form, self.control = form, control
            self.events = SimpleNamespace(loaded=threading.Event())

        def evaluate_js(self, source):
            """Evaluate from a background caller while the native UI thread keeps pumping."""
            response, submitted = [], threading.Event()
            def evaluate():
                try:
                    response.append(self.control.ExecuteScriptAsync(source))
                except Exception as error:
                    response.append(error)
                finally:
                    submitted.set()
            self.form.BeginInvoke(Action(evaluate))
            if not submitted.wait(10):
                raise TimeoutError('The desktop window did not respond')
            task = response[0]
            if isinstance(task, Exception):
                raise task
            if not task.Wait(10000):
                raise TimeoutError('The page did not return a result')
            return json.loads(str(task.Result))

        def destroy(self):
            self.form.BeginInvoke(Action(self.form.Close))

    def run():
        form = None
        try:
            Application.EnableVisualStyles()
            form = Form()
            form.Text = 'IOP Runtime'
            form.ClientSize = Size(1360, 900)
            form.MinimumSize = Size(860, 620)
            form.StartPosition = FormStartPosition.CenterScreen
            form.AutoScaleMode = AutoScaleMode.Dpi
            form.Icon = Icon(str(Path(__file__).with_name('ui') / 'mark.ico'))
            control = WebView2()
            control.Dock = DockStyle.Fill
            properties = CoreWebView2CreationProperties()
            properties.UserDataFolder = str(storage)
            control.CreationProperties = properties
            form.Controls.Add(control)
            window = Window(form, control)

            def message(_sender, args):
                value = json.loads(str(args.TryGetWebMessageAsString()))
                if value.get('action') == 'open_browser':
                    open_browser(str(value.get('view', 'overview')))

            def external(_sender, args):
                args.Handled = True
                webbrowser.open(str(args.Uri))

            def loaded(_sender, args):
                if not args.IsSuccess:
                    errors.append(RuntimeError('The desktop page could not load: ' + str(args.WebErrorStatus)))
                    form.Close()
                    return
                control.ExecuteScriptAsync("window.pywebview={api:{open_browser:(view)=>{window.chrome.webview.postMessage(JSON.stringify({action:'open_browser',view}));return Promise.resolve(true)}}};window.dispatchEvent(new Event('pywebviewready'));")
                if not window.events.loaded.is_set():
                    window.events.loaded.set()
                    if on_loaded:
                        threading.Thread(target=on_loaded, args=(window,), daemon=True).start()

            def initialized(_sender, args):
                if not args.IsSuccess:
                    errors.append(RuntimeError(str(args.InitializationException)))
                    form.Close()
                    return
                control.CoreWebView2.WebMessageReceived += message
                control.CoreWebView2.NewWindowRequested += external
                control.CoreWebView2.NavigationCompleted += loaded
                control.CoreWebView2.Navigate(url)

            control.CoreWebView2InitializationCompleted += initialized
            form.Shown += lambda *_: control.EnsureCoreWebView2Async(None)
            Application.Run(form)
        except BaseException as error:
            errors.append(error)
        finally:
            if form is not None:
                form.Dispose()

    thread = Thread(ThreadStart(run))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()
    dll_directory.close()
    if errors:
        raise errors[0]
