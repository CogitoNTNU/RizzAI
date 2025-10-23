# 🎯 RizzAI Frontend Components

This directory contains all React components for the RizzAI web application.

## Components

### ImageUpload.js
- Drag-and-drop image upload
- File validation
- Image preview
- Accepts: PNG, JPG, GIF (up to 10MB)

### OpeningLineGenerator.js
- Displays 3 generated opening lines
- Shows generation parameters (temperature, max tokens)
- Interactive selection with hover effects
- Click handler for kiss animation

### KissAnimation.js
- Animated kiss emojis (💋 😘 💕 💖 ❤️ 💗)
- Floating animation from bottom to top
- Random positioning and timing
- Auto-cleanup after 3 seconds

## Styling

All components use Tailwind CSS utility classes for styling:
- Gradient backgrounds
- Smooth transitions
- Responsive design
- Hover effects
- Loading states

## Customization

### Colors
Edit `tailwind.config.js` to modify the color scheme.

### Animations
Adjust animation timing in `tailwind.config.js`:
```javascript
animation: {
  'float': 'float 2s ease-in-out forwards',
}
```

### Kiss Emojis
Modify the emoji array in `KissAnimation.js`:
```javascript
['💋', '😘', '💕', '💖', '❤️', '💗']
```
