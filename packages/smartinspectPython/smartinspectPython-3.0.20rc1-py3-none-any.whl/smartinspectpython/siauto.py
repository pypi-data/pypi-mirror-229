"""
Module: siauto.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description      |
| ---------- | ----------- | -----------------|
| 2023/05/30 | 3.0.0.0     | Initial Version. | 

</details>

Provides automatically created objects for using SmartInspect Python logging.  

The following classes are imported when `from smartinspectpython.siauto import *` is specified:  
- SIArgumentNullException
- SIArgumentOutOfRangeException
- SIAuto
- SIColors
- SIConfigurationTimer
- SIControlCommandEventArgs
- SIErrorEventArgs
- SIFilterEventArgs
- SIInfoEventArgs
- SILevel
- SILogEntryEventArgs
- SIProcessFlowEventArgs
- SISession
- SIWatchEventArgs
- SmartInspectException
"""

# all classes to import when "import *" is specified.
__all__ = [
    'SIArgumentNullException',
    'SIArgumentOutOfRangeException',
    'SIAuto',
    'SIColors',
    'SIConfigurationTimer',
    'SIControlCommandEventArgs',
    'SIErrorEventArgs',
    'SIFilterEventArgs',
    'SIInfoEventArgs',
    'SILevel',
    'SILogEntryEventArgs',
    'SIProcessFlowEventArgs',
    'SISession',
    'SIWatchEventArgs',
    'SmartInspectException'
]

import os

# our package imports.
from .siargumentnullexception import SIArgumentNullException
from .siargumentoutofrangeexception import SIArgumentOutOfRangeException
from .sicolor import SIColors
from .siconfigurationtimer import SIConfigurationTimer
from .sicontrolcommandeventargs import SIControlCommandEventArgs
from .sierroreventargs import SIErrorEventArgs
from .sifiltereventargs import SIFilterEventArgs
from .siinfoeventargs import SIInfoEventArgs
from .silevel import SILevel
from .silogentryeventargs import SILogEntryEventArgs
from .siprocessfloweventargs import SIProcessFlowEventArgs
from .sisession import SISession
from .siutils import static_init
from .siwatcheventargs import SIWatchEventArgs
from .smartinspect import SmartInspect
from .smartinspectexception import SmartInspectException


@static_init    # indicate we have a static init method.
class SIAuto:
    """
    Provides automatically created objects for using the SmartInspect and SISession classes.

    This class provides a static property called Si of type SmartInspect.
    Furthermore a SISession instance named Main with Si as parent is ready to use. The siauto module 
    is especially useful if you do not want to create SmartInspect and SISession instances by yourself.

    The SmartInspect.Connections property of Si is set to "tcp(host=localhost)", the
    SmartInspect.AppName property to "Auto" and the SISession.Name property to "Main".

    Threadsafety:
        The public static members of this class are thread-safe.

    **Example:**
    ``` python
    # Use the following for 1-time initialization code:

    from .smartinspectpython.siauto import *
    SIAuto.Si.Connections = 'tcp(host=yourdns.com)'
    SIAuto.Si.Enabled = True               # connect
    SIAuto.Main.Level = SILevel.Debug      # set logging level to Debug (ALL msgs)
    #SIAuto.Main.Level = SILevel.Verbose   # set logging level to Verbose
    #SIAuto.Main.Level = SILevel.Message   # set logging level to Message
    #SIAuto.Main.Level = SILevel.Warning   # set logging level to Warning
    #SIAuto.Main.Level = SILevel.Error     # set logging level to Error

    # Use the following in main (or classes) in your project:

    # get logger reference.
    _logsi:SISession = SIAuto.Main
    
    # log some messages and data.
    _logsi.LogSystem(SILevel.Debug)
    _logsi.LogDebug("This is a Debug message.")
    _logsi.LogMessage("This is a Message.")
    _logsi.LogWarning("You have been warned!")
    _logsi.LogError("Danger Will Robinson!")
    ```
    """

    """
    ## Static Properties
    """

    # static properties.
    Si:SmartInspect = None   
    """ 
    SmartInspect logging instance (automatically created). 
    """

    Main:SISession = None
    """ 
    SmartInspect logging Session instance ('Main', automatically created). 

    The SISession.Name is set to "Main" and the SISession.Parent to SIAuto.Si.

    **Example:**
    ``` python
    # Use the following in main (or classes) in your project:

    # get logger reference.
    from .smartinspectpython.siauto import *
    _logsi:SISession = SIAuto.Main
    
    # log some messages and data.
    _logsi.LogSystem(SILevel.Debug)
    _logsi.LogDebug("This is a Debug message.")
    _logsi.LogMessage("This is a Message.")
    _logsi.LogWarning("You have been warned!")
    _logsi.LogError("Danger Will Robinson!")
    ```
    """

    """
    ## Methods
    """

    @classmethod
    def static_init(cls) -> None:
        """ 
        Initializes a new static instance of the class.
        """
        # Note - at this point, you cannot call any of the static methods in this class,
        # as we are still in the initilization phase!

        # create a new smartinspect instance, using the
        # entry point name as the appname.
        cls.Si = SmartInspect(os.path.basename(os.sys.argv[0]))

        # set default connections string, logging levels, and disable by default.
        cls.Si.Connections = 'tcp(host=localhost)'
        cls.Si.Enabled = False
        cls.Si.Level = SILevel.Debug
        cls.Si.DefaultLevel = SILevel.Debug

        # create new default session, named "Main".
        cls.Main = cls.Si.AddSession('Main', True)
        cls.Main.Level = SILevel.Debug
