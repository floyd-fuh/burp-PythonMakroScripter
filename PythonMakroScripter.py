from java.awt import Font
from javax.swing import JScrollPane, JTextPane
from javax.swing.text import SimpleAttributeSet

# TODO: can we load this list dynamically? For now we are missing out on new features...
from burp import IBurpCollaboratorClientContext, IBurpCollaboratorInteraction, IBurpExtender, IBurpExtenderCallbacks, IContextMenuFactory, IContextMenuInvocation, ICookie, IExtensionHelpers, IExtensionStateListener, IHttpListener, IHttpRequestResponse, IHttpRequestResponsePersisted, IHttpRequestResponseWithMarkers, IHttpService, IInterceptedProxyMessage, IIntruderAttack, IIntruderPayloadGenerator, IIntruderPayloadGeneratorFactory, IIntruderPayloadProcessor, IMenuItemHandler, IMessageEditor, IMessageEditorController, IMessageEditorTab, IMessageEditorTabFactory, IParameter, IProxyListener, IRequestInfo, IResponseInfo, IResponseKeywords, IResponseVariations, IScanIssue, IScannerCheck, IScannerInsertionPoint, IScannerInsertionPointProvider, IScannerListener, IScanQueueItem, IScopeChangeListener, ISessionHandlingAction, ITab, ITempFile, ITextEditor

import base64
import traceback

class BurpExtender(IBurpExtender, ISessionHandlingAction, IExtensionStateListener, ITab):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.helpers

        self.scriptpane = JTextPane()
        self.scriptpane.setFont(Font('Monospaced', Font.PLAIN, 11))

        self.scrollpane = JScrollPane()
        self.scrollpane.setViewportView(self.scriptpane)

        self._code = compile('', '<string>', 'exec')
        self._script = ''

        script = callbacks.loadExtensionSetting('script')

        if script:
            script = base64.b64decode(script)

            self.scriptpane.document.insertString(
                self.scriptpane.document.length,
                script,
                SimpleAttributeSet())

            self._script = script
            self._code = compile(script, '<string>', 'exec')

        callbacks.registerExtensionStateListener(self)
        callbacks.customizeUiComponent(self.getUiComponent())
        callbacks.registerSessionHandlingAction(self)
        callbacks.addSuiteTab(self)
        self.scriptpane.requestFocus()
    
    def extensionUnloaded(self):
        try:
            self.callbacks.saveExtensionSetting(
                'script', base64.b64encode(self._script))
        except Exception:
            traceback.print_exc(file=self.callbacks.getStderr())
        return
    
    def getActionName(self):
        return "Custom Makro Python Script"
    
    def performAction(self, currentRequest, macroItems):
        try:
            globals_ = {'extender': self,
                        'callbacks': self.callbacks,
                        'helpers': self.helpers,
                        'IBurpCollaboratorClientContext': IBurpCollaboratorClientContext,
                        'IBurpCollaboratorInteraction': IBurpCollaboratorInteraction,
                        'IBurpExtender': IBurpExtender,
                        'IBurpExtenderCallbacks': IBurpExtenderCallbacks,
                        'IContextMenuFactory': IContextMenuFactory,
                        'IContextMenuInvocation': IContextMenuInvocation,
                        'ICookie': ICookie,
                        'IExtensionHelpers': IExtensionHelpers,
                        'IExtensionStateListener': IExtensionStateListener,
                        'IHttpListener': IHttpListener,
                        'IHttpRequestResponse': IHttpRequestResponse,
                        'IHttpRequestResponsePersisted': IHttpRequestResponsePersisted,
                        'IHttpRequestResponseWithMarkers': IHttpRequestResponseWithMarkers,
                        'IHttpService': IHttpService,
                        'IInterceptedProxyMessage': IInterceptedProxyMessage,
                        'IIntruderAttack': IIntruderAttack,
                        'IIntruderPayloadGenerator': IIntruderPayloadGenerator,
                        'IIntruderPayloadGeneratorFactory': IIntruderPayloadGeneratorFactory,
                        'IIntruderPayloadProcessor': IIntruderPayloadProcessor,
                        'IMenuItemHandler': IMenuItemHandler,
                        'IMessageEditor': IMessageEditor,
                        'IMessageEditorController': IMessageEditorController,
                        'IMessageEditorTab': IMessageEditorTab,
                        'IMessageEditorTabFactory': IMessageEditorTabFactory,
                        'IParameter': IParameter,
                        'IProxyListener': IProxyListener,
                        'IRequestInfo': IRequestInfo,
                        'IResponseInfo': IResponseInfo,
                        'IResponseKeywords': IResponseKeywords,
                        'IResponseVariations': IResponseVariations,
                        'IScanIssue': IScanIssue,
                        'IScannerCheck': IScannerCheck,
                        'IScannerInsertionPoint': IScannerInsertionPoint,
                        'IScannerInsertionPointProvider': IScannerInsertionPointProvider,
                        'IScannerListener': IScannerListener,
                        'IScanQueueItem': IScanQueueItem,
                        'IScopeChangeListener': IScopeChangeListener,
                        'ISessionHandlingAction': ISessionHandlingAction,
                        'ITab': ITab,
                        'ITempFile': ITempFile,
                        'ITextEditor': ITextEditor,
            }
            locals_  = {'currentRequest': currentRequest,
                        'macroItems': macroItems
            }
            exec(self.script, globals_, locals_)
        except Exception:
            traceback.print_exc(file=self.callbacks.getStderr())
        return

    def getTabCaption(self):
        return 'Makro Script'

    def getUiComponent(self):
        return self.scrollpane

    @property
    def script(self):
        end = self.scriptpane.document.length
        _script = self.scriptpane.document.getText(0, end)

        if _script == self._script:
            return self._code

        self._script = _script
        self._code = compile(_script, '<string>', 'exec')
        return self._code