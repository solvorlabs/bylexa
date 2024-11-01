import React from 'react';
import { motion } from 'framer-motion';

const WaveAnimation: React.FC = () => {
  const waveVariants = {
    animate: {
      scale: [1, 1.5, 1],
      opacity: [0.7, 1, 0.7],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
  };

  return (
    <div className="flex space-x-2 mb-4">
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          className="w-4 h-16 bg-cyan-500 rounded"
          variants={waveVariants}
          animate="animate"
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  );
};

export default WaveAnimation;
