import React from 'react';
import styles from './styles/DeleteModal.module.css';

interface DeleteModalProps {
  onConfirm: () => void;
  onCancel: () => void;
  type: string; // The type of entity being destroyed (e.g., 'Cell', 'Link')
}

// In a system built on reversible operations, deletion is a profound and irreversible act.
// This modal serves as the final gateway before destroying a piece of the GVM's state,
// ensuring the user understands the consequence of moving from a recoverable state to a non-recoverable one.
const DeleteModal: React.FC<DeleteModalProps> = ({ onConfirm, onCancel, type }) => {
  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <h2 className={styles.modalTitle}>Are you sure?</h2>
        <p className={styles.modalDescription}>
          Do you really want to delete this {type}? This action cannot be undone and represents
          an irreversible state transition.
        </p>

        <div className={styles.buttonGroup}>
          <button onClick={onConfirm} className={`${styles.buttonBase} ${styles.yesButton}`}>
            Yes, proceed with irreversible deletion
          </button>
          <button onClick={onCancel} className={`${styles.buttonBase} ${styles.noButton}`}>
            No, maintain current state
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal;