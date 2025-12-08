# Barcode Scanner Setup Guide

## Overview
The PCB Testing System supports automatic PCB ID capture via barcode scanners. Most USB barcode scanners work as keyboard input devices, making integration seamless.

## How It Works

1. **Automatic Focus**: When you open the Start Test or Advanced Test window, the PCB ID field is automatically focused and ready to receive input.

2. **Scan Process**: 
   - Point the barcode scanner at the PCB's barcode
   - Press the scanner trigger
   - The barcode data is automatically entered into the PCB ID field
   - Most scanners send an Enter key after scanning, which triggers confirmation

3. **Visual Feedback**:
   - 📷 "Ready to scan" - Field is ready for barcode input
   - ✓ "ID captured" - Barcode has been successfully scanned
   - ✓ "Barcode scanned" - Scan confirmed (after Enter key)

## Barcode Scanner Configuration

### Recommended Settings
Most USB barcode scanners work out-of-the-box, but ensure these settings:

1. **Suffix Character**: Configure scanner to send "Enter" (CR/LF) after each scan
2. **Prefix Character**: None (or remove if present)
3. **USB HID Mode**: Keyboard emulation mode
4. **Symbology**: Enable the barcode types used on your PCBs (Code 39, Code 128, QR, etc.)

### Testing Your Scanner

1. Open Notepad or any text editor
2. Scan a barcode
3. Verify that:
   - The barcode data appears correctly
   - Cursor moves to next line (Enter key sent)
   - No extra characters appear

## Supported Barcode Types

The system accepts any alphanumeric PCB ID. Common barcode symbologies:
- Code 39
- Code 128
- QR Code
- Data Matrix
- EAN/UPC

## Workflow

### Basic Test Workflow
1. Open "Start Test" window
2. Scan PCB barcode (auto-fills PCB ID)
3. Enter or read test parameters
4. Click "Run Test"
5. After test completes, click "Clear" to prepare for next PCB
6. PCB ID field auto-focuses for next scan

### Advanced Test Workflow
1. Open "Advanced Test" window
2. Scan PCB barcode (auto-fills PCB ID)
3. Select test sequence from dropdown
4. Click "Run Test Sequence"
5. After test completes, click "Clear" to prepare for next PCB
6. PCB ID field auto-focuses for next scan

## Troubleshooting

### Scanner Not Working
- **Check USB Connection**: Ensure scanner is properly connected
- **Driver Installation**: Some scanners require drivers (check manufacturer website)
- **Test in Notepad**: Verify scanner works in other applications
- **Check Configuration**: Ensure scanner is in USB HID keyboard mode

### Wrong Characters Appearing
- **Keyboard Layout**: Scanner may be configured for different keyboard layout
- **Reconfigure Scanner**: Use manufacturer's configuration barcodes to set correct layout

### No Enter Key After Scan
- **Configure Suffix**: Use manufacturer's setup barcode to add CR/LF suffix
- **Manual Confirmation**: Press Enter manually after scanning

### Multiple Scans Required
- **Scan Speed**: Scan more slowly or hold scanner steady
- **Distance**: Adjust distance between scanner and barcode
- **Lighting**: Ensure adequate lighting on barcode

## Best Practices

1. **Label Placement**: Place barcodes in consistent, easily accessible locations on PCBs
2. **Barcode Quality**: Use high-quality printed barcodes with good contrast
3. **Barcode Size**: Ensure barcodes are large enough for reliable scanning (minimum 1cm height)
4. **Operator Training**: Train operators on proper scanning technique
5. **Scanner Maintenance**: Keep scanner lens clean for optimal performance

## Recommended Scanners

### Budget Options
- Honeywell Voyager 1200g (~$100)
- Zebra DS2208 (~$150)
- Datalogic QuickScan QD2430 (~$120)

### Industrial Options
- Zebra DS8178 (~$400) - Rugged, wireless
- Honeywell Xenon 1900 (~$350) - High performance
- Datalogic Gryphon GD4500 (~$300) - Industrial grade

All recommended scanners support USB HID keyboard emulation and require no special drivers.

## Integration Notes

The system uses standard keyboard input capture, so any device that emulates keyboard input will work:
- USB barcode scanners
- Bluetooth barcode scanners (in HID mode)
- Handheld terminals
- Mobile apps with keyboard wedge functionality

No additional software or drivers are required beyond what the scanner manufacturer provides.
