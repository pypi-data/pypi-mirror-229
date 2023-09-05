# rasp-modules
Modules for Raspberry PI LCD, MCP3008.

This package will provide you with basic modules for communications between LCD, MCP3008 with raspberry PI. I will add new modules soon!.

## Installtaion:
```
pip install rasp-modules
```

## Usage:
 import the LCD for Display and import MCP3008 for analogue communication.

#### LCD
  ```python
   from display.lcd import LCD
  
   lcd = LCD(5, 6, 12, 13, 16, 19)
   or
   lcd = LCD(rs=5, en=6, d4=12, d5=13, d6=16, d7=19)

   lcd.cursor_start(0, 0)
   lcd.print_line(f"testing")  # "Message string
  ```

#### MCP3008
  ```python
   from analogue.mcp3008 import MCP3008
  
   adc_mcp3008 = MCP3008(max_speed_hz=1_000_000)
  
   lcd.cursor_start(0, 0)
   lcd.print_line(adc_mcp3008)  # "Message string
  ```
