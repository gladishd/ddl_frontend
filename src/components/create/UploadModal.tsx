import React, { useState, useContext, useEffect, ChangeEvent } from 'react';
import styles from './styles/UploadModal.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import MediaPlayer from '@/utils/MediaPlayer'; // Assuming this utility is migrated
import { getMediaSrc } from '@/utils/utils'; // Assuming this utility is migrated

interface UploadModalProps {
  uploadType: 'image' | 'audio';
  setIsModalOpen: (isOpen: boolean) => void;
}

// The UploadModal facilitates the attachment of a semantic payload (image, audio, video) to a Cell or Group.
// This is not mere decoration; it enriches the state of a GVM element with observable data that can
// inform user interactions or programmatic behavior.
const UploadModal: React.FC<UploadModalProps> = ({ uploadType, setIsModalOpen }) => {
  const {
    updateSituationAndNode,
    updateGroup,
    selectedSituation,
    selectedGroup,
    loading
  } = useContext(CanvasContext);

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  // ... (useEffect hook to set initial preview would go here) ...

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    setErrorMessage('');
    setFile(null);
    setPreview(null);

    if (selectedFile) {
      // This is a local-only validation, a pre-check before the transaction to
      // attach the media is attempted.
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (selectedFile.size > maxSize) {
        setErrorMessage(`File size exceeds 50MB limit.`);
        return;
      }
      // ... (rest of file type validation logic) ...

      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSave = async () => {
    if (!file || loading) return;

    const formData = new FormData();
    formData.append(uploadType, file);

    try {
      if (selectedSituation?._id) {
        await updateSituationAndNode(selectedSituation._id, formData);
      } else if (selectedGroup) {
        await updateGroup(selectedGroup._id, formData);
      }
      setIsModalOpen(false);
    } catch (error) {
      console.error(`Error updating ${uploadType}:`, error);
      setErrorMessage('An error occurred during upload. The transaction was reversed.');
    }
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <h2 className={styles.modalTitle}>Upload {uploadType === 'image' ? 'Image' : 'Media'}</h2>
        <label htmlFor="file-upload" className={`${styles.buttonBase} ${styles.uploadButton}`}>
          {preview ? 'Change File' : 'Select File'}
        </label>
        <input
          id="file-upload"
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          accept={uploadType === 'image' ? 'image/*' : 'audio/*,video/*'}
          disabled={loading}
        />
        {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}
        {preview && (
          <div className={styles.previewContainer}>
            {uploadType === 'image' ? (
              <img src={getMediaSrc(preview)} alt="Preview" className={styles.previewImage} />
            ) : (
              <MediaPlayer src={getMediaSrc(preview)} autoplay={false} className={styles.previewMedia} />
            )}
          </div>
        )}
        <div className={styles.buttonGroup}>
          <button onClick={handleSave} className={`${styles.buttonBase} ${styles.saveButton}`} disabled={!file || loading}>
            {loading ? 'Saving...' : 'Save'}
          </button>
          <button onClick={() => setIsModalOpen(false)} className={`${styles.buttonBase} ${styles.cancelButton}`} disabled={loading}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;