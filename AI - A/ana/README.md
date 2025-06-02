# Ana AI Assistant

Ana is a cross-platform AI assistant with a semi-realistic animated character, voice integration, smart assistant logic, and a futuristic cyberpunk-inspired UI.

![Ana AI Assistant](assets/character/idle.png)

## Features

- 🤖 **Intelligent Assistant**: Powered by OpenAI's GPT models
- 🗣️ **Voice Integration**: Speak and listen with ElevenLabs voice synthesis
- 📝 **Task Management**: Add, update, delete, and complete tasks
- 📅 **Calendar Integration**: Google Calendar sync (requires OAuth setup)
- 🎵 **Music Control**: Play and control music from YouTube Music and Spotify
- 🧠 **Contextual Memory**: Long-term memory stored locally with optional cloud backup
- 🚀 **Self-Evolution**: Ability to debug itself and generate new features
- 🌙 **Customizable UI**: Dark/light mode with cyberpunk-inspired circuit design
- 🔄 **Auto-Updates**: Check for and apply updates automatically

## Installation

### Prerequisites

- Python 3.8 or higher
- ElevenLabs API key (for voice)
- OpenAI API key (for intelligence)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ana-ai.git
   cd ana-ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Create a copy of `config.example.json` as `config.json`
   - Add your ElevenLabs and OpenAI API keys

4. Run Ana:
   ```
   python main.py
   ```

## Configuration

Ana can be configured through the settings UI or by editing the configuration file:

- **Voice**: Select different voices from ElevenLabs
- **Theme**: Choose between dark and light mode
- **Animations**: Enable/disable character animations
- **Features**: Enable/disable specific features
- **Developer Mode**: Access advanced debugging options

## Usage

- **Voice Commands**: Activate by clicking the microphone button or saying "Hey Ana"
- **Tasks**: Manage your to-do list with voice or text commands
- **Calendar**: View and add events to your calendar
- **Music**: Control your music playback with voice commands
- **Questions**: Ask Ana anything for intelligent responses

## Development

Ana is designed to be extended with new features. The modular architecture allows for:

- **Custom Commands**: Add new command patterns in `intent_parser.py`
- **UI Themes**: Create custom themes in `theme_manager.py`
- **New Features**: Add new functionality through the module system
- **Self-Evolution**: Ana can generate code for new features using the OpenAI API

## License

[MIT License](LICENSE)

## Acknowledgements

- OpenAI for GPT API
- ElevenLabs for voice technology
- PyQt5 for UI framework 