// This component renders the semantic payload (audio/video) of a Cell or Group.
// The act of playing the media is an 'observation' of the element's state,
// making its embedded knowledge accessible to the user.
'use client';

import React, { useMemo } from 'react';

interface MediaPlayerProps {
  src: string;
  className?: string;
  autoplay?: boolean;
}

const MediaPlayer: React.FC<MediaPlayerProps> = ({ src, className, autoplay = false }) => {
  const isVideo = useMemo(() => {
    // A simple check to determine if the source is a video file.
    // In a real system, this would be more robust, likely checking MIME types.
    const videoExtensions = ['.mp4', '.webm', '.ogg'];
    return videoExtensions.some(ext => src.toLowerCase().endsWith(ext)) || src.startsWith('data:video');
  }, [src]);

  if (isVideo) {
    return (
      <video src={src} className={className} autoPlay={autoplay} controls muted loop>
        Your browser does not support the video tag.
      </video>
    );
  }

  return (
    <audio src={src} className={className} autoPlay={autoplay} controls>
      Your browser does not support the audio element.
    </audio>
  );
};

export default MediaPlayer;