import React, { useEffect, useState } from 'react';

function KissAnimation() {
  const [kisses, setKisses] = useState([]);

  useEffect(() => {
    // Generate random kisses
    const newKisses = [];
    for (let i = 0; i < 30; i++) {
      newKisses.push({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 1,
        emoji: ['💋', '😘', '💕', '💖', '❤️', '💗'][Math.floor(Math.random() * 6)],
        size: 20 + Math.random() * 30,
      });
    }
    setKisses(newKisses);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {kisses.map((kiss) => (
        <div
          key={kiss.id}
          className="absolute bottom-0 animate-float"
          style={{
            left: `${kiss.left}%`,
            animationDelay: `${kiss.delay}s`,
            fontSize: `${kiss.size}px`,
          }}
        >
          {kiss.emoji}
        </div>
      ))}
    </div>
  );
}

export default KissAnimation;
