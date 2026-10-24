const SAVE_BUTTON_FEEDBACK = {
  committed: { action: 'save', label: 'Save campaign' },
  pending: { action: 'wait', label: 'Saving campaign' },
  failed: { action: 'export-unsaved', label: 'Save failed. Export your unsaved campaign' },
};

export function saveButtonFeedback(kind) {
  return SAVE_BUTTON_FEEDBACK[kind] || SAVE_BUTTON_FEEDBACK.committed;
}
