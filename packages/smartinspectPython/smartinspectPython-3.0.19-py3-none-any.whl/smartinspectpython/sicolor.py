"""
Module: sicolor.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/05/30 | 3.0.0.0     | Initial Version.  

</details>
"""

from argparse import ArgumentError
from enum import Enum

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIColor:
    """
    Mimics the System.Drawing.Color class functionality.
    """

    # NOTE : The "zero" pattern (all members being 0) must represent
    #      : "not set". This allows "Color c;" to be correct.
    _StateKnownColorValid: int = 0x0001
    _StateARGBValueValid: int = 0x0002
    _StateValueMask: int = _StateARGBValueValid
    _StateNameValid: int = 0x0008
    _NotDefinedValue: int = 0

    # shift counts and bit masks for A, R, G, B components in ARGB mode.
    _ARGBAlphaShift: int = 24
    _ARGBRedShift: int = 16
    _ARGBGreenShift: int = 8
    _ARGBBlueShift: int = 0

    _ARGBAlphaMask: int = 0xFF << _ARGBAlphaShift
    _ARGBRedMask: int = 0xFF << _ARGBRedShift
    _ARGBGreenMask: int = 0xFF << _ARGBGreenShift
    _ARGBBlueMask: int = 0xFF << _ARGBBlueShift

    _MaxValueUInt: int = 0xFFFFFFFF  # 4294967295
    _MaxValueByte: int = 0xFF        # 255

    _InvalidEx2BoundArgument: str = "Color Value of '{1}' is not valid for '{0}'. '{0}' should be greater than or equal to {2} and less than or equal to {3}.";
    

    def __init__(self, value: int) -> None:
        """
        Initializes a new instance of the class using a supplied known color value
        that represents the four ARGB components (alpha, red, green, and blue).

        Args:
            value (int):
                Integer value that represents the ARGB components of the color.
        """

        # initialize instance.
        #self.__init__(value, SIColor._StateNameValid, "FromValue", "")
        self._InitializeWithState(value, SIColor._StateNameValid, "FromValue", "")


    #@overload
    #def __init__(self, value: int, state: int, name: str, knownColor: str) -> None:
    #    """
    #    Initializes a new instance of the class.

    #    Args:
    #        value
    #            Integer value that represents the ARGB components of the color.
    #        state
    #            The state in which the SIColor object is to be placed at initialization.
    #        name
    #            Name of a pre-defined common color value.
    #        knownColor
    #            Pre-defined known color object, or None if not a known color.
    #    """

    #    if (value == None):
    #        value = 0

    #    # validations.
    #    if (value > SIColor._MaxValueUInt):
    #        raise ArgumentError(None, SIColor._InvalidEx2BoundArgument.format("value", value, 0, SIColor._MaxValueUInt))

    #    # initialize instance.
    #    self._fValue: int = value
    #    self._fName: str = name


    @property
    def A(self) -> int:
        """
        Gets the alpha component value of this color structure.

        0 is fully transparent, and 255 is fully opaque.
        """
        return ((self._fValue >> SIColor._ARGBAlphaShift) & SIColor._MaxValueByte)


    @property
    def B(self) -> int:
        """
        Gets the blue component value of this SIColor structure.
        """
        return ((self._fValue >> SIColor._ARGBBlueShift) & SIColor._MaxValueByte)


    @property
    def G(self) -> int:
        """
        Gets the green component value of this SIColor structure.
        """
        return ((self._fValue >> SIColor._ARGBGreenShift) & SIColor._MaxValueByte)


    @property
    def Name(self) -> str:
        """ 
        Gets the name of the color, if it's a known color value.
        """
        return self._fName


    @property
    def R(self) -> int:
        """
        Gets the red component value of this SIColor structure.
        """
        return ((self._fValue >> SIColor._ARGBRedShift) & SIColor._MaxValueByte)


    @property
    def Value(self) -> int:
        """ 
        Gets the raw value of the color in integer form.
        """
        return self._fValue
        #private long Value
        #{
        #    get
        #    {
        #        if ((state & StateValueMask) != 0)
        #        {
        #            return value;
        #        }

        #        // This is the only place we have system colors value exposed
        #        if (IsKnownColor)
        #        {
        #            return KnownColorTable.KnownColorToArgb((KnownColor)knownColor);
        #        }

        #        return NotDefinedValue;
        #    }
        #}


    #@Value.setter
    #def Value(self, value: int):
    #    """ 
    #    Sets the value.
    #    """
    #    if value == None:
    #        self._fValue = SIColor.NotDefinedValue
    #    else:
    #        self._fValue = value


    @property
    def ValueHex(self) -> int:
        """ 
        Gets the raw value of the color in hexadecimal form.

        Returns a string value in the form of 0xAARRBBGG (e.g. 0x00FF0000).
        """
        return "0x" + "{:08x}".format(self._fValue).upper()


    def _InitializeWithState(self, value: int, state: int, name: str, knownColor: str) -> None:
        """
        Initializes a new instance of the class.

        Args:
            value (int):
                The raw value of the color in integer form.
            state (int):
                The state of the color assignment (e.g. _StateNameValid, etc).
            name (str):
                The name of the color assignment type (e.g. "FromValue", etc).
            knownColor (str):
                The known color value, if it's a known color value.
        """

        if (value == None):
            value = 0

        # validations.
        if (value > SIColor._MaxValueUInt):
            raise ArgumentError(None, SIColor._InvalidEx2BoundArgument.format("value", value, 0, SIColor._MaxValueUInt))

        # initialize instance.
        self._fValue: int = value
        self._fName: str = name


    @staticmethod
    def _MakeArgb(alpha: int, red: int, green: int, blue: int) -> int:
        """
        Creates a SIColor structure from the four ARGB component (alpha, red, green, and blue) values. 
        Although this method allows a 32-bit value to be passed for each component, the value of each 
        component is limited to 8 bits.

        Args:
            alpha (int):
                The alpha component. Valid values are 0 (fully transparent) through 255 (fully opaque).
            red (int):
                The red component. Valid values are 0 through 255.
            green (int):
                The green component. Valid values are 0 through 255.
            blue (int):
                The blue component. Valid values are 0 through 255.

        Returns:
            The SIColor that this method creates.

        Raises:
            ArgumentError:
                alpha, red, green, or blue is less than 0 or greater than 255.
            
        """
        return (red << 16 | green << 8 | blue | alpha << 24) & SIColor._MaxValueUInt


    @staticmethod
    def CheckByte(value: int, name: str) -> None:
        """
        Ensures the value for the named parameter (A,R,G, or B) is between 0 through 255.

        Args:
            value (int):
                The value to check.
            name (str):
                The descriptove name of the value, used to identify the value in case of an exception.
        """
        if (value < 0) or (value > SIColor._MaxValueByte):
            raise ArgumentError(None, SIColor._InvalidEx2BoundArgument.format(name, value, 0, 0xFF))


    @staticmethod
    def FromArgb(alpha: int, red: int, green: int, blue: int):
        """
        Creates a SIColor structure from the four ARGB component (alpha, red, green, and blue) values. 
        Although this method allows a 32-bit value to be passed for each component, the value of each 
        component is limited to 8 bits.

        Args:
            alpha (int):
                The alpha component. Valid values are 0 (fully transparent) through 255 (fully opaque).
            red (int):
                The red component. Valid values are 0 through 255.
            green (int):
                The green component. Valid values are 0 through 255.
            blue (int):
                The blue component. Valid values are 0 through 255.

        Returns:
            The SIColor that this method creates.

        Raises:
            ArgumentException:
                alpha, red, green, or blue is less than 0 or greater than 255.
        """

        # validations.
        SIColor.CheckByte(alpha, "alpha")
        SIColor.CheckByte(red, "red")
        SIColor.CheckByte(green, "green")
        SIColor.CheckByte(blue, "blue")

        # create color object and set properties as to how its value was derived.
        oColor = SIColor(SIColor._MakeArgb(alpha, red, green, blue))
        oColor._fName = "FromArgb"
        return oColor


    @staticmethod
    def FromRgb(red: int, green: int, blue: int):
        """
        Creates a SIColor structure from the three RGB component (red, green, and blue) values. 
        Although this method allows a 32-bit value to be passed for each component, the value of each 
        component is limited to 8 bits.  The alpha value is implicitly 255 (fully opaque). 

        Args:
            red (int):
                The red component. Valid values are 0 through 255.
            green (int):
                The green component. Valid values are 0 through 255.
            blue (int):
                The blue component. Valid values are 0 through 255.

        Returns:
            The SIColor that this method creates.

        Raises:
            ArgumentException:
                red, green, or blue is less than 0 or greater than 255.
        """
        
        # create color object and set properties as to how its value was derived.
        oColor = SIColor.FromArgb(0, red, green, blue)
        oColor._fName = "FromRgb"
        return oColor


    def ToArgb(self) -> int:
        """
        Gets the 32-bit ARGB value of this color structure.
        """
        return self._fValue


    def __str__(self) -> str:
        """
        Converts this color structure to a human-readable string.

        Returns:
            A string that consists of the ARGB component names and their values.
        """
        result = "Color Name \"{6}\": [A={0}, R={1}, G={2}, B={3}], Value={4} ({5})".format(self.A, self.R, self.G, self.B, self.Value, self.ValueHex, self.Name)
        return result 


        #public bool IsKnownColor => (state & StateKnownColorValid) != 0;

        #public bool IsEmpty => state == 0;

        #public bool IsNamedColor => ((state & StateNameValid) != 0) || IsKnownColor;

        #public bool IsSystemColor => IsKnownColor && IsKnownColorSystem((KnownColor)knownColor);


@export
class SIColors(Enum):
    """
    Pre-defined known color values.
    """
    
    AliceBlue = 0xFFF0F8FF
    """ System-defined color that has an ARGB value of #FFF0F8FF. """

    AntiqueWhite = 0xFFFAEBD7
    """ <summary>Gets a system-defined color that has an ARGB value of #FFFAEBD7. """

    Coral = 0xFFFF7F50
    """Gets a system-defined color that has an ARGB value of #FFFF7F50."""

    CornflowerBlue = 0xFF6495ED
    """Gets a system-defined color that has an ARGB value of #FF6495ED."""

    DarkBlue = 0xFF00008B
    """Gets a system-defined color that has an ARGB value of #FF00008B."""

    DarkCyan = 0xFF008B8B
    """Gets a system-defined color that has an ARGB value of #FF008B8B."""

    DarkGray = 0xFFA9A9A9
    """Gets a system-defined color that has an ARGB value of #FFA9A9A9."""

    DarkOrange = 0xFFFF8C00
    """Gets a system-defined color that has an ARGB value of #FFFF8C00."""

    DeepSkyBlue = 0xFF00BFFF
    """Gets a system-defined color that has an ARGB value of #FF00BFFF."""
    
    DimGray = 0xFF696969
    """Gets a system-defined color that has an ARGB value of #FF696969."""

    ForestGreen = 0xFF228B22
    """Gets a system-defined color that has an ARGB value of #."""

    Gainsboro = 0xFFDCDCDC
    """Gets a system-defined color that has an ARGB value of #FFDCDCDC."""

    Gold = 0xFFFFD700
    """Gets a system-defined color that has an ARGB value of #."""

    Green = 0xFF008000
    """Gets a system-defined color that has an ARGB value of #FF008000."""

    Khaki = 0xFFF0E68C
    """Gets a system-defined color that has an ARGB value of #FFF0E68C."""

    Lavender = 0xFFE6E6FA
    """Gets a system-defined color that has an ARGB value of #FFE6E6FA."""

    LightBlue = 0xFFADD8E6
    """Gets a system-defined color that has an ARGB value of #FFADD8E6."""

    LightCoral = 0xFFF08080
    """Gets a system-defined color that has an ARGB value of #FFF08080."""

    LightGreen = 0xFF90EE90
    """Gets a system-defined color that has an ARGB value of #FF90EE90."""

    LightGray = 0xFFD3D3D3
    """Gets a system-defined color that has an ARGB value of #FFD3D3D3."""

    LightSkyBlue = 0xFF87CEFA
    """Gets a system-defined color that has an ARGB value of #FF87CEFA."""

    Orange = 0xFFFFA500
    """Gets a system-defined color that has an ARGB value of #FFFFA500."""

    Red = 0xFFFF0000
    """Gets a system-defined color that has an ARGB value of #FFFF0000."""

    SaddleBrown = 0xFF8B4513
    """Gets a system-defined color that has an ARGB value of #FF8B4513."""

    SeaGreen = 0xFF2E8B57
    """Gets a system-defined color that has an ARGB value of #FF2E8B57."""

    Silver = 0xFFC0C0C0
    """Gets a system-defined color that has an ARGB value of #FFC0C0C0."""

    SkyBlue = 0xFF87CEEB
    """Gets a system-defined color that has an ARGB value of #FF87CEEB."""

    SlateGray = 0xFF708090
    """Gets a system-defined color that has an ARGB value of #FF708090."""

    Tan = 0xFFD2B48C
    """Gets a system-defined color that has an ARGB value of #FFD2B48C."""

    White = 0xFFFFFFFF
    """Gets a system-defined color that has an ARGB value of #FFFFFFFF."""

    WhiteSmoke = 0xFFF5F5F5
    """Gets a system-defined color that has an ARGB value of #FFF5F5F5."""

    Yellow = 0xFFFFFF00
    """Gets a system-defined color that has an ARGB value of #FFFFFF00."""
