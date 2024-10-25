import uno


def DeActivate():
    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    service = "com.sun.star.frame.DispatchHelper"
    dispatcher = smgr.createInstanceWithContext(service, ctx)

    args1 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    args1.Name = "TrackChanges"
    args1.Value = False

    document = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame()
    dispatcher.executeDispatch(document, ".uno:TrackChanges", "", 0, (args1,))
    
def Activate():
    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    service = "com.sun.star.frame.DispatchHelper"
    dispatcher = smgr.createInstanceWithContext(service, ctx)

    args1 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    args1.Name = "TrackChanges"
    args1.Value = True

    document = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame()
    dispatcher.executeDispatch(document, ".uno:TrackChanges", "", 0, (args1,))

    
def Show():
    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    service = "com.sun.star.frame.DispatchHelper"
    dispatcher = smgr.createInstanceWithContext(service, ctx)

    args1 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    args1.Name = "ShowTrackedChanges"
    args1.Value = True

    document = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame()
    dispatcher.executeDispatch(document, ".uno:ShowTrackedChanges", "", 0, (args1,))



def AcceptAll(tracked:bool=True,comments:bool=True):
    try:
        ctx = XSCRIPTCONTEXT.getComponentContext()
        smgr = ctx.getServiceManager()
        service = "com.sun.star.frame.DispatchHelper"
        dispatcher = smgr.createInstanceWithContext(service, ctx)
        document = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame()
        dispatcher.executeDispatch(document, ".uno:Save", "", 0, ())
        if comments:
            dispatcher.executeDispatch(document, ".uno:DeleteAllNotes", "", 0, ())
        if tracked:
            dispatcher.executeDispatch(document, ".uno:AcceptAllTrackedChanges", "", 0, ())
        
        dispatcher.executeDispatch(document, ".uno:Save", "", 0, ())
        return True
    except:
        return False


def Finalize():
    return AcceptAll(True,True)

def ActiveSpell():
    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.getServiceManager()
    service = "com.sun.star.frame.DispatchHelper"
    dispatcher = smgr.createInstanceWithContext(service, ctx)

    args1 = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    args1.Name = "Enable"
    args1.Value = True

    document = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame()
    dispatcher.executeDispatch(document, ".uno:SpellOnline", "", 0, (args1,))



g_exportedScripts = (Activate,DeActivate,Show,AcceptAll,Finalize,ActiveSpell )