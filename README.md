# ColorVisionAid (CVA)

ColorVisionAid is a software application designed to assist individuals with color blindness in distinguishing between colors they commonly confuse. The software utilizes real-time image processing through a camera to highlight specific colors and provide visual guidance to the user.

## 🚀 Quick Start

### **Desktop Version (Recommended):**
```bash
python CVA.py
```

This is the main, stable version with full features using PyQt5 interface.

## Features

- **Real-Time Color Detection:** Advanced algorithm highlights red, green, blue, and yellow colors
- **Color Blindness Support:** Specialized modes for different types of color vision deficiency  
- **Customizable Settings:** Adjust sensitivity, contrast, and detection parameters
- **Screenshot Gallery:** Save and manage screenshots within the application
- **Multi-Language Support:** English and Turkish language support

## Installation & Setup

### **Windows (Recommended):**
```bash
# Run the setup script
setup_mobile.bat

# Or manual installation:
pip install -r requirements.txt          # For desktop
pip install -r requirements_mobile.txt   # For mobile
```

### **Linux/macOS:**
```bash
chmod +x setup_mobile.sh
./setup_mobile.sh
```

## Usage

### Desktop Version (`CVA.py`):
1. Run `python CVA.py`
2. Professional GUI with full controls
3. Camera feed with real-time color detection
4. Settings panel for customization
5. Gallery for screenshot management

### Mobile Version (`mobile_opencv.py`):
## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- OpenCV-compatible camera

### Setup
1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python CVA.py
   ```

## Usage

### Basic Controls
- **Color Selection:** Click on color buttons to enable/disable specific color detection
- **Sensitivity:** Adjust detection sensitivity with the slider
- **Color Blindness Type:** Select your specific type from the dropdown menu
- **Screenshot:** Capture and save screenshots using the camera icon
- **Settings:** Access advanced configuration options

### Supported Color Blindness Types
- **Protanopia:** Red-blind (missing L-cones)
- **Deuteranopia:** Green-blind (missing M-cones)  
- **Tritanopia:** Blue-blind (missing S-cones)
- **Red-Green:** General red-green confusion
- **Blue-Yellow:** Blue-yellow confusion

## Technical Details

- **Core Algorithm:** Advanced HSV color space analysis with adaptive thresholding
- **Supported Platforms:** Windows, Linux, macOS
- **Camera Support:** USB webcams, built-in cameras, external devices
- **Performance:** Optimized for real-time processing (15-30 FPS)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For any questions or suggestions, please contact me at bayirammar@gmail.com