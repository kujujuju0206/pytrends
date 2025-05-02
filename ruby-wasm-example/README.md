# Keyword Volume Analyzer with Ruby.wasm and Chart.js

This project demonstrates how to use Ruby.wasm and Chart.js to create a browser-based application for analyzing keyword search volumes across different platforms. It's a port of a Python-based application that originally used server-side processing.

## Features

- **100% Client-Side Processing**: All data processing happens in the browser using Ruby.wasm
- **Interactive Charts**: Visualize keyword trends using Chart.js
- **Multiple Platforms**: Support for Google, YouTube, X (Twitter), and TikTok
- **API Integration**: Optional integration with the Keyword Tool API
- **Data Export**: Export results to CSV format
- **Responsive Design**: Works on desktop and mobile devices

## Examples

The project includes two examples:

1. **Basic Example** (`index.html`): A simple implementation showing the core functionality
2. **Advanced Example** (`advanced.html`): A full-featured implementation with improved UI, API support, and CSV export

## How It Works

### Ruby.wasm

Ruby.wasm is a WebAssembly port of the Ruby programming language. It allows running Ruby code directly in the browser without a server-side Ruby interpreter. This project uses Ruby.wasm to:

- Process user inputs
- Generate or fetch keyword data
- Analyze and transform data for visualization
- Handle CSV export

### Chart.js

Chart.js is a JavaScript library for creating interactive charts. This project uses Chart.js to:

- Visualize keyword volume trends over time
- Create line charts with multiple datasets
- Provide interactive tooltips and legends

## Getting Started

1. Clone this repository
2. Install dependencies: `npm install`
3. Start the server: `node server.js`
4. Open your browser and navigate to `http://localhost:12000/menu`

## API Integration

The advanced example supports integration with the [Keyword Tool API](https://keywordtool.io/api). To use this feature:

1. Sign up for a Keyword Tool API account
2. Get your API key
3. Enter your API key in the advanced example
4. Search for keywords to fetch real data

Without an API key, the application will use generated demo data.

## Technical Details

- **Ruby.wasm Version**: 3.4
- **Chart.js Version**: Latest (CDN)
- **Browser Compatibility**: Works in all modern browsers that support WebAssembly

## Comparison with Python Version

This browser-based version offers several advantages over the original Python implementation:

- **No Server Required**: Everything runs in the browser
- **Instant Deployment**: No need to set up a Python environment
- **Better User Experience**: Faster response times and no page reloads
- **Offline Capability**: Can work without an internet connection (when using demo data)

## License

MIT