# Ana AI Assistant

A cross-platform AI assistant with cyberpunk aesthetics and a focus on privacy and security.

## Features

- **Full Screen Character Mode**: Ana character visualization in full screen with animated backgrounds
- **Weather Integration**: Background and greetings change based on current weather conditions
- **End-to-End Encryption**: All data remains on your device with AES-256 encryption
- **Privacy-Preserving API Calls**: No data stored externally, anonymized identifiers
- **Cyberpunk Aesthetics**: Procedurally generated character visualization with cyberpunk design
- **Voice Engine**: Supports both local TTS (pyttsx3) and premium voices (ElevenLabs)
- **Health Monitoring**: Integration with health tracking including steps, sleep, heart rate
- **Customizable UI**: Sidebar navigation system with dedicated health dashboard

## Installation

1. Clone the repository:
```
git clone https://github.com/your-repo/ana-ai.git
cd ana-ai
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python -m ana.main
```

## Full Screen Character Mode

The new full screen character mode displays Ana in full screen with dynamic backgrounds that can change based on:
- Current weather conditions
- Time of day
- User preferences

To activate full screen mode, click the "Full Screen Mode" button in the character view.

## Weather Integration

Ana can now:
- Display weather-themed backgrounds in full screen mode
- Include current weather information in greetings
- Adjust the character's appearance based on weather conditions

## Security Features

- All data is stored locally with AES-256 encryption
- No user data is sent to external services
- API calls are anonymized and include "do not store" instructions
- GitHub tokens and API credentials are stored securely

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
