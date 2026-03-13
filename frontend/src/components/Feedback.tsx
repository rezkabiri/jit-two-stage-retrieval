// frontend/src/components/Feedback.tsx
import React, { useState } from 'react';

interface FeedbackProps {
  messageId: string;
  onFeedback: (id: string, rating: 'up' | 'down') => void;
}

const Feedback: React.FC<FeedbackProps> = ({ messageId, onFeedback }) => {
  const [selected, setSelected] = useState<'up' | 'down' | null>(null);

  const handleFeedback = (rating: 'up' | 'down') => {
    if (selected) return; // Prevent multiple feedbacks for the same message
    setSelected(rating);
    onFeedback(messageId, rating);
  };

  return (
    <div className="feedback-container">
      <button
        className={`feedback-btn ${selected === 'up' ? 'active' : ''}`}
        onClick={() => handleFeedback('up')}
        disabled={!!selected}
        title="Thumbs Up"
      >
        👍
      </button>
      <button
        className={`feedback-btn ${selected === 'down' ? 'active' : ''}`}
        onClick={() => handleFeedback('down')}
        disabled={!!selected}
        title="Thumbs Down"
      >
        👎
      </button>
    </div>
  );
};

export default Feedback;
