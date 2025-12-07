# CS4182 Jeep Game

A 3D Jeep game built with Python and OpenGL featuring a jeep, obstacles, collectibles, and multiple lighting/shading models.

## Features

- 3D Jeep environment with textured roads and grass
- Multiple camera views (top, front, behind, free rotation)
- Collision detection with obstacles
- Collectible stars and special items (diamond)
- Acceleration ribbons for speed boosts
- Street lamps with lighting effects
- Multiple lighting modes (ambient, point, directional, spotlight)
- Blinn-Phong shader support
- Fullscreen mode
- Loading screen and home screen

## Requirements

### For Running the Executable (Recommended)
- Windows OS
- **No additional installation required** - the executable is standalone

### For Running from Source
The project requires Python 3.x with the following dependencies listed in [src/requirements.txt](src/requirements.txt):

- PyOpenGL
- PyOpenGL-accelerate
- numpy
- Pillow (PIL)

## Installation

### Option 1: Run Pre-built Executable (Windows) - **EASIEST METHOD**

**No installation needed!** Simply navigate to the `dist` folder and double-click:

```
dist/main.exe
```

The executable is standalone and includes all required dependencies.

### Option 2: Install Python Dependencies (For running from source)

```bash
pip install -r src/requirements.txt
```

Or install individually:

```bash
pip install PyOpenGL PyOpenGL-accelerate numpy Pillow
```

## Running the Game

### Option 1: Run Pre-built Executable (Windows) - **RECOMMENDED**

Simply double-click the executable:

```
dist/main.exe
```

Or from command line:

```bash
cd dist
main.exe
```

### Option 2: Run from Source

Navigate to the `src` directory and run:

```bash
cd src
python main.py
```

## Controls

### Movement
- **Arrow Keys** or **WASD**: Move the jeep
  - Up/W: Forward
  - Down/S: Backward
  - Left/A: Left
  - Right/D: Right

### Camera Views
- **2**: Behind view (default following view)
- **5**: Top-down view
- **8**: Front view
- **R**: Reset view to default

### Camera Control
- **Left Mouse + Drag**: Rotate camera around jeep
- **Mouse Wheel**: Zoom in/out
- **M**: Toggle object manipulation mode (drag stars with mouse)

### Display
- **F**: Toggle fullscreen
- **H**: Show/hide help window

### Lighting
- **Right-click**: Open lighting menu
  - Ambient Light
  - Point Light
  - Directional Light
  - Spotlight (follows jeep)
  - Toggle Lamp Lights
  - Toggle Blinn-Phong Shader
  - No Lighting

### Game
- **Space**: Start game from home screen

## Gameplay

1. **Starting**: Press Space on the home screen to begin
2. **Objective**: Navigate the jeep to the finish line while collecting stars
3. **Avoid**: Orange cones - hitting them ends the game
4. **Collect**: 
   - Yellow stars (worth points)
   - Diamond (reduces score penalty by half)
   - Acceleration ribbons (temporary speed boost)
5. **Stay on Track**: Going off-road ends the game

## Scoring

- Time-based scoring (starts after countdown)
- Collect all stars for maximum points
- Diamond provides a score bonus
- Acceleration ribbons help you complete faster

## Project Structure

```
project/
├── src/
│   ├── main.py              # Main game file
│   ├── jeep.py              # Jeep model
│   ├── cone.py              # Obstacle cone
│   ├── star.py              # Collectible star
│   ├── diamond.py           # Special diamond item
│   ├── ribbon.py            # Acceleration ribbon
│   ├── streetlamp.py        # Street lamp
│   ├── ImportObject.py      # OBJ file loader
│   ├── shader_utils.py      # Shader utilities
│   └── requirements.txt     # Python dependencies
├── shaders/
│   ├── blinn_phong.vert     # Vertex shader
│   └── blinn_phong.frag     # Fragment shader
├── img/                     # Textures and images
├── objects/                 # 3D models (.obj, .mtl)
├── dist/
│   └── main.exe             # **Standalone executable (READY TO RUN)**
├── build/                   # Build artifacts
└── game.spec                # PyInstaller specification
```

## Building an Executable (Optional)

The executable is already included in the `dist/` folder. If you need to rebuild it:

```bash
pyinstaller game.spec
```

The new executable will be created in the `dist/` directory.

## Troubleshooting

### Executable Won't Start
- Make sure all game assets (img/, objects/, shaders/ folders) are in the correct locations relative to the executable
- Try running as administrator if you encounter permission issues
- Check Windows Defender or antivirus - they may block the executable initially

### Missing Textures
Ensure the `img/` folder is in the correct location relative to the executable or source files.

### Shader Errors
If Blinn-Phong shaders fail to load, the game will fall back to fixed-function pipeline lighting.

### Performance Issues
- Try disabling lamp lights (right-click menu)
- Reduce window size or exit fullscreen mode
- Disable advanced shading

### OpenGL Errors
Make sure your graphics drivers are up to date and support OpenGL 2.1+.

## Credits

Developed for CS4182 course project.

## License

Educational project - all rights reserved.