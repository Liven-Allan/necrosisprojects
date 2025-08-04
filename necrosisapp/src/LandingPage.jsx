import React, { useRef, useState, useEffect } from 'react';
import { FaCloudUploadAlt, FaFolderOpen, FaUserCircle, FaHistory, FaSearch, FaDownload, FaChevronLeft, FaChevronRight, FaEye, FaEyeSlash, FaTimes, FaTrash, FaCog, FaSignOutAlt, FaMinus, FaUser } from 'react-icons/fa';
import './LandingPage.css';
import cassavaIcon from '../../UI files/cassava.png';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * LandingPage component provides UI for uploading images via drag-and-drop or file browsing.
 * Selected images are previewed above the upload area, which shrinks and sticks to the bottom after selection.
 * When users log in, they start with a fresh new session instead of loading previous analysis results.
 */
const LandingPage = () => {
  // State to hold selected image files
  const [selectedImages, setSelectedImages] = useState([]);
  // State to control if upload area should shrink and stick to bottom
  const [isUploaded, setIsUploaded] = useState(false);
  // Ref for hidden file input
  const fileInputRef = useRef(null);
  // State to show results view
  const [showResults, setShowResults] = useState(false);
  // State for pagination
  const [resultsPage, setResultsPage] = useState(0);
  // Number of cards per page
  const CARDS_PER_PAGE = 2;
  const [showUploadContainer, setShowUploadContainer] = useState(true);
  const [pendingImages, setPendingImages] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showUserAccount, setShowUserAccount] = useState(false);
  const [userSessions, setUserSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [sessionsError, setSessionsError] = useState('');
  const navigate = useNavigate();
  // State to hold backend analysis results
  const [analysisResults, setAnalysisResults] = useState([]);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  // State for zoomed image index (null means modal closed)
  const [zoomedImageIndex, setZoomedImageIndex] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [currentSessionDate, setCurrentSessionDate] = useState(null);
  const [historyLoadingSession, setHistoryLoadingSession] = useState(null);
  const [toast, setToast] = useState({ message: '', type: '' });
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileContact, setProfileContact] = useState('');
  const [profileOrganisation, setProfileOrganisation] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileNeedsAttention, setProfileNeedsAttention] = useState(false);

  // Show toast helper
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast({ message: '', type: '' }), 2500);
  };

  // Get logged-in user's email and username from localStorage
  const userEmail = localStorage.getItem('userEmail') || '';
  const username = localStorage.getItem('username') || '';

  // Initialize fresh session on mount (login) - no longer loads previous session results
  useEffect(() => {
    const initializeNewSession = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      // Start with a fresh new session instead of loading previous results
      // This ensures users always start with a clean slate when they log in
      setSelectedImages([]);
      setPendingImages([]);
      setAnalysisResults([]);
      setShowResults(false);
      setIsUploaded(false);
      setCurrentSessionId(null);
      setCurrentSessionDate(null);
      setResultsPage(0);
      setShowUploadContainer(true);
      // Show welcome message for new session
      showToast('Welcome! Ready for a new analysis session.', 'success');
    };
    initializeNewSession();
    // eslint-disable-next-line
  }, []);

  // Fetch user sessions when history popup is opened
  useEffect(() => {
    if (showHistory) {
      const fetchSessions = async () => {
        setSessionsLoading(true);
        setSessionsError('');
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
          const res = await axios.get('/api/user_sessions/', {
            headers: { Authorization: `Token ${token}` },
          });
          setUserSessions(res.data.sessions || []);
        } catch (err) {
          setSessionsError('Failed to load analysis history.');
        }
        setSessionsLoading(false);
      };
      fetchSessions();
    }
  }, [showHistory]);

  // Fetch user profile info for badge on mount
  useEffect(() => {
    if (username) {
      axios.get(`/api/user/${username}/`, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` },
      })
        .then(res => {
          setProfileNeedsAttention(!res.data.contact || !res.data.organisation);
        })
        .catch(() => {
          setProfileNeedsAttention(true);
        });
    }
    // eslint-disable-next-line
  }, []);

  // Fetch user profile info when modal opens
  useEffect(() => {
    if (showProfileModal && username) {
      setProfileLoading(true);
      axios.get(`/api/user/${username}/`, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` },
      })
        .then(res => {
          setProfileContact(res.data.contact || '');
          setProfileOrganisation(res.data.organisation || '');
        })
        .catch(() => {
          setProfileContact('');
          setProfileOrganisation('');
        })
        .finally(() => setProfileLoading(false));
    }
  }, [showProfileModal, username]);

  // Live update badge state when editing fields
  useEffect(() => {
    setProfileNeedsAttention(!profileContact || !profileOrganisation);
  }, [profileContact, profileOrganisation]);

  // Handle file selection from file input or drop
  const handleFiles = (files) => {
    const imageFiles = Array.from(files).filter(file =>
      /image\/(jpeg|png|jpg)/.test(file.type)
    );
    if (imageFiles.length > 0) {
      if (showResults) {
        setPendingImages(prev => [...prev, ...imageFiles]);
      } else {
        setSelectedImages(prev => [...prev, ...imageFiles]);
        setIsUploaded(true);
      }
    }
  };

  // Handle drag-and-drop
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleFiles(e.dataTransfer.files);
  };

  // Handle drag over
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  // Handle click on 'Browse Files'
  const handleBrowseClick = () => {
    fileInputRef.current.click();
  };

  // Handle file input change
  const handleFileChange = (e) => {
    handleFiles(e.target.files);
    e.target.value = '';
  };

  // Handle submit button click
  const handleSubmit = async () => {
    if ((showResults && pendingImages.length > 0) || (!showResults && selectedImages.length > 0)) {
      setAnalysisLoading(true);
      setAnalysisError('');
      // Collect images to send
      const imagesToSend = showResults ? pendingImages : selectedImages;
      const formData = new FormData();
      imagesToSend.forEach((file) => {
        formData.append('images', file);
      });
      // If session is active, send session_id
      if (currentSessionId) {
        formData.append('session_id', currentSessionId);
      }
      try {
        const token = localStorage.getItem('token');
        const res = await axios.post('/api/analyze/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            ...(token && { Authorization: `Token ${token}` }),
          },
        });
        // Append new results to existing ones
        setAnalysisResults(prev => [...prev, ...res.data.results]);
        setShowResults(true);
        setResultsPage(0);
        // Update session state from response
        setCurrentSessionId(res.data.session_id);
        setCurrentSessionDate(res.data.created_at);
        if (showResults) {
          setSelectedImages((prev) => [...prev, ...pendingImages]);
          setPendingImages([]);
        }
        showToast('New analysis started!', 'success');
      } catch (err) {
        setAnalysisError('Failed to analyze images. Please try again.');
        showToast('Failed to analyze images. Please try again.', 'error');
      }
      setAnalysisLoading(false);
    } else {
      setShowResults(true);
      setResultsPage(0);
    }
  };

  // Handler for 'Add New Analysis' button
  const handleAddNewAnalysis = () => {
    setSelectedImages([]);
    setPendingImages([]);
    setAnalysisResults([]);
    setShowResults(false);
    setIsUploaded(false);
    setCurrentSessionId(null);
    setCurrentSessionDate(null);
    setResultsPage(0);
    setShowHistory(false);
    setShowUploadContainer(true); // Ensure upload UI is visible
    showToast('Ready for a new analysis session!', 'success');
  };

  // Handle download results (placeholder)
  const handleDownload = () => {
    alert('Download results!');
  };

  // Pagination handlers (updated for backend results)
  const totalPages = Math.ceil(analysisResults.length / CARDS_PER_PAGE);
  const pagedResults = showResults
    ? analysisResults.slice(resultsPage * CARDS_PER_PAGE, (resultsPage + 1) * CARDS_PER_PAGE)
    : [];
  const handlePrevPage = () => {
    setResultsPage((prev) => (prev > 0 ? prev - 1 : prev));
  };
  const handleNextPage = () => {
    setResultsPage((prev) => (prev < totalPages - 1 ? prev + 1 : prev));
  };

  // Generate mock analysis results for each image
  const getMockResults = (img, idx) => ({
    name: img.name || `image${idx + 1}.png`,
    lesions: Math.floor(Math.random() * 40) + 10,
    percentage: `${Math.floor(Math.random() * 60) + 20}%`,
  });

  // Get images for current page
  const pagedImages = showResults
    ? selectedImages.slice(resultsPage * CARDS_PER_PAGE, (resultsPage + 1) * CARDS_PER_PAGE)
    : [];

  // Remove image from preview
  const handleRemoveImage = (idx) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== idx));
    if (selectedImages.length === 1) setIsUploaded(false);
  };

  // Mock history data
  const historyData = [
    { id: 1, date: '2024-06-10 14:30', images: 24 },
    { id: 2, date: '2024-06-09 10:15', images: 12 },
  ];

  // Log out handler
  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        await axios.post('/api/delete_session_images/', {}, {
          headers: { Authorization: `Token ${token}` },
        });
      } catch (err) {
        // Ignore errors
      }
    }
    localStorage.removeItem('userEmail');
    localStorage.removeItem('token');
    setShowUserAccount(false);
    // Remove images from UI but keep text results
    setAnalysisResults(prev => prev.map(r => ({ ...r, result_image: null })));
    setSelectedImages([]);
    setPendingImages([]);
    setShowResults(true);
    navigate('/'); // Go back to login page
  };

  // Handler for trash bin click
  const handleDeleteClick = (session) => {
    setSessionToDelete(session);
    setShowDeleteModal(true);
    setDeleteError('');
  };

  // Handler for confirming deletion
  const handleConfirmDelete = async () => {
    if (!sessionToDelete) return;
    setDeleteError('');
    const token = localStorage.getItem('token');
    try {
      await axios.delete(`/api/sessions/${sessionToDelete.session_id}/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setUserSessions((prev) => prev.filter((s) => s.session_id !== sessionToDelete.session_id));
      setShowDeleteModal(false);
      setSessionToDelete(null);
      showToast('Session deleted successfully!', 'success');
      // If the deleted session is the one currently being viewed, reset to new session state
      if (currentSessionId === sessionToDelete.session_id) {
        setSelectedImages([]);
        setPendingImages([]);
        setAnalysisResults([]);
        setShowResults(false);
        setIsUploaded(false);
        setCurrentSessionId(null);
        setCurrentSessionDate(null);
        setResultsPage(0);
        setShowHistory(false);
        setShowUploadContainer(true);
      }
    } catch (err) {
      setDeleteError('Failed to delete session.');
    }
  };

  // Handler for canceling deletion
  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setSessionToDelete(null);
    setDeleteError('');
  };

  // Handler to fetch and show results for a session from history
  const handleShowSessionResults = async (session) => {
    setHistoryLoadingSession(session.session_id);
    setAnalysisError('');
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`/api/session_results/${session.session_id}/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setAnalysisResults(res.data.results || []);
      setCurrentSessionId(res.data.session_id);
      setCurrentSessionDate(res.data.created_at);
      setShowResults(true);
      setSelectedImages([]);
      setPendingImages([]);
      setResultsPage(0);
      setShowHistory(false);
      setShowUploadContainer(true); // Always show upload UI after loading session
      showToast('Session results loaded. You can upload more images to this session.', 'success');
    } catch (err) {
      setAnalysisError('Failed to load session results.');
      showToast('Failed to load session results.', 'error');
    }
    setHistoryLoadingSession(null);
  };

  // Keyboard navigation for zoom modal
  useEffect(() => {
    if (zoomedImageIndex === null) return;
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setZoomedImageIndex(null);
      if (e.key === "ArrowLeft") setZoomedImageIndex((prev) => prev === 0 ? analysisResults.length - 1 : prev - 1);
      if (e.key === "ArrowRight") setZoomedImageIndex((prev) => prev === analysisResults.length - 1 ? 0 : prev + 1);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [zoomedImageIndex, analysisResults.length]);

  // CSV download handler
  const handleDownloadResultsCSV = () => {
    if (!analysisResults || analysisResults.length === 0) return;
    const headers = ['Image Name', 'Total Lesions', 'Necrosis Percentage'];
    const rows = analysisResults.map(r => [
      r.filename,
      r.lesion_count,
      Number(r.percentage_necrosis).toFixed(2) + '%',
    ]);
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(val => '"' + String(val).replace(/"/g, '""') + '"').join(',')),
    ].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    // Format date for filename
    let filename = 'analysis_results.csv';
    if (currentSessionDate) {
      const d = new Date(currentSessionDate);
      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      filename = `${yyyy}-${mm}-${dd}_analysis_results.csv`;
    }
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`landing-root${isUploaded ? ' landing-root-uploaded' : ''}`}>
      {/* Zoomed Image Modal with navigation */}
      {zoomedImageIndex !== null && analysisResults[zoomedImageIndex] && (
        <div className="zoom-modal" onClick={() => setZoomedImageIndex(null)}>
          <div className="zoom-modal-content" onClick={e => e.stopPropagation()}>
            <button className="zoom-modal-close" onClick={() => setZoomedImageIndex(null)} title="Close zoomed image">
              <FaTimes size={32} color="#d32f2f" />
            </button>
            {/* Navigation arrows and counter on top */}
            {analysisResults.length > 1 && (
              <div className="zoom-modal-nav-row">
                <button
                  className="zoom-modal-arrow left"
                  onClick={() => setZoomedImageIndex(zoomedImageIndex === 0 ? analysisResults.length - 1 : zoomedImageIndex - 1)}
                  title="Previous image"
                >
                  <FaChevronLeft size={36} />
                </button>
                <span className="zoom-modal-counter-label">{zoomedImageIndex + 1} of {analysisResults.length}</span>
                <button
                  className="zoom-modal-arrow right"
                  onClick={() => setZoomedImageIndex(zoomedImageIndex === analysisResults.length - 1 ? 0 : zoomedImageIndex + 1)}
                  title="Next image"
                >
                  <FaChevronRight size={36} />
                </button>
              </div>
            )}
            <img
              src={analysisResults[zoomedImageIndex].result_image}
              alt={analysisResults[zoomedImageIndex].filename}
              className="zoom-modal-img"
            />
          </div>
        </div>
      )}
      {/* Top Bar */}
      <div className="landing-topbar">
        <div className="landing-topbar-left">
          <div className="cassava-icon">
            <img src={cassavaIcon} alt="Cassava Root" style={{ width: 32, height: 32 }} />
          </div>
          <span className="landing-title">CASSAVA NECROSIS ANALYSER</span>
        </div>
        <div className="landing-topbar-right" style={{ position: 'relative' }}>
          <div className="image-count-badge" title="Number of images in analysis">{analysisResults.length}</div>
          <button className="icon-btn" title="Analysis History" onClick={() => setShowHistory(true)}>
            <FaHistory size={24} />
          </button>
          <button className="icon-btn" title="User Account" onClick={() => setShowUserAccount(true)} style={{ position: 'relative' }}>
            <FaUserCircle size={24} />
            {profileNeedsAttention && (
              <span className="profile-badge-attention" title="Profile incomplete">!</span>
            )}
          </button>
          {/* Analysis History Popup */}
          {showHistory && (
            <>
              <div className="popup-backdrop" onClick={() => setShowHistory(false)} />
              <div className="history-popup-dropdown">
              {/* Top section */}
              <div className="history-popup-top">
                <FaHistory size={20} className="history-popup-clock" />
                <span className="history-popup-title">Analysis History</span>
                <button className="history-popup-close" onClick={() => setShowHistory(false)}>
                  <FaTimes size={18} />
                </button>
              </div>
              {/* Scrollable blocks */}
              <div className="history-popup-scroll">
                <div className="history-block add-new" onClick={handleAddNewAnalysis} style={{ cursor: 'pointer' }}>Add New Analysis</div>
                {sessionsLoading && <div className="history-block">Loading...</div>}
                {sessionsError && <div className="history-block" style={{ color: 'red' }}>{sessionsError}</div>}
                {userSessions.map((item) => (
                  <div
                    className={`history-block${historyLoadingSession === item.session_id ? ' loading' : ''}`}
                    key={item.session_id}
                    onClick={() => handleShowSessionResults(item)}
                    style={{ cursor: 'pointer', opacity: historyLoadingSession === item.session_id ? 0.6 : 1 }}
                  >
                    <div className="history-block-left">
                      <div className="history-block-date">{new Date(item.created_at).toLocaleString()}</div>
                      <div className="history-block-images">{item.num_images} images analyzed</div>
                    </div>
                    <button
                      className="history-block-trash"
                      title="Delete"
                      onClick={e => { e.stopPropagation(); handleDeleteClick(item); }}
                      disabled={historyLoadingSession === item.session_id}
                    >
                      <FaTrash size={16} />
                    </button>
                    {historyLoadingSession === item.session_id && <span style={{ marginLeft: 8 }}><span className="spinner" /></span>}
                  </div>
                ))}
              </div>
            </div>
            </>
          )}
          {/* User Account Popup */}
          {showUserAccount && (
            <>
              <div className="popup-backdrop" onClick={() => setShowUserAccount(false)} />
              <div className="user-popup-dropdown">
              {/* Top section */}
              <div className="user-popup-top">
                <FaUserCircle size={20} className="user-popup-icon" />
                <span className="user-popup-email">{userEmail}</span>
                <button className="user-popup-close" onClick={() => setShowUserAccount(false)}>
                  <FaTimes size={18} />
                </button>
              </div>
              <div className="user-popup-divider" />
                {/* Profile item */}
                <div className="user-popup-section user-popup-profile" onClick={() => { setShowProfileModal(true); setShowUserAccount(false); }} style={{ cursor: 'pointer', position: 'relative' }}>
                  <FaUser size={18} className="user-popup-section-icon" />
                  <span className="user-popup-section-text">Profile</span>
                  {profileNeedsAttention && (
                    <span className="profile-badge-attention" style={{ marginLeft: 8 }} title="Profile incomplete">!</span>
                  )}
                </div>
                {/* Settings item */}
              <div className="user-popup-section user-popup-settings">
                <FaCog size={18} className="user-popup-section-icon" />
                <span className="user-popup-section-text">Settings</span>
              </div>
              <div className="user-popup-section user-popup-logout" onClick={handleLogout} style={{ cursor: 'pointer' }}>
                <FaSignOutAlt size={18} className="user-popup-section-icon" />
                <span className="user-popup-section-text">Log Out</span>
                </div>
              </div>
            </>
          )}
          {/* Profile Modal */}
          {showProfileModal && (
            <div className="modal-overlay" onClick={() => setShowProfileModal(false)}>
              <div className="modal profile-modal" onClick={e => e.stopPropagation()}>
                <div className="modal-title" style={{ color: '#066D12' }}>Profile</div>
                <button className="zoom-modal-close" onClick={() => setShowProfileModal(false)} title="Close profile" style={{ position: 'absolute', top: 16, right: 16 }}>
                  <FaTimes size={28} color="#d32f2f" />
                </button>
                <div className="profile-fields">
                  <div className="profile-row">
                    <span className="profile-label">Username</span>
                    <span className="profile-value">{username}</span>
                  </div>
                  <div className="profile-row">
                    <span className="profile-label">Email</span>
                    <span className="profile-value">{userEmail}</span>
                  </div>
                  <div className="profile-row">
                    <span className="profile-label">Contact {(!profileContact && profileNeedsAttention) && <span className="profile-badge-attention" title="Required">!</span>}</span>
                    <input
                      className="profile-value profile-input"
                      type="text"
                      value={profileContact}
                      onChange={e => setProfileContact(e.target.value)}
                      placeholder="Enter contact info"
                      disabled={profileLoading || profileSaving}
                      style={{ minWidth: 0, flex: 1 }}
                    />
                  </div>
                  <div className="profile-row">
                    <span className="profile-label">Organisation {(!profileOrganisation && profileNeedsAttention) && <span className="profile-badge-attention" title="Required">!</span>}</span>
                    <input
                      className="profile-value profile-input"
                      type="text"
                      value={profileOrganisation}
                      onChange={e => setProfileOrganisation(e.target.value)}
                      placeholder="Enter organisation/affiliation"
                      disabled={profileLoading || profileSaving}
                      style={{ minWidth: 0, flex: 1 }}
                    />
                  </div>
                </div>
                <div className="profile-modal-actions">
                  <button
                    className="modal-btn modal-confirm"
                    disabled={profileLoading || profileSaving}
                    onClick={async () => {
                      setProfileSaving(true);
                      try {
                        await axios.patch(`/api/user/${username}/`, {
                          contact: profileContact,
                          organisation: profileOrganisation,
                        }, {
                          headers: { Authorization: `Token ${localStorage.getItem('token')}` },
                        });
                        showToast('Profile updated!', 'success');
                        setShowProfileModal(false);
                      } catch (err) {
                        showToast('Failed to update profile.', 'error');
                      }
                      setProfileSaving(false);
                    }}
                  >
                    {profileSaving ? 'Updating...' : 'Update'}
                  </button>
                </div>
                {profileLoading && <div style={{ textAlign: 'center', marginTop: 18 }}>Loading...</div>}
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Main Content */}
      <div className="landing-content-wide">
        {/* Hide main title when images are uploaded or results are shown */}
        {!isUploaded && !showResults && (
          <h1 className="landing-main-title">CASSAVA NECROSIS ANALYSER</h1>
        )}
        {/* Results View */}
        {showResults ? (
          <div className="landing-results-view">
            {/* Pending images preview row and submit button if there are pending images */}
            {pendingImages.length > 0 && (
              <>
                <div className="landing-image-preview-row landing-image-preview-row-large">
                  {pendingImages.map((img, idx) => (
                    <div className="landing-image-preview-item landing-image-preview-item-large" key={idx}>
                      <img
                        src={URL.createObjectURL(img)}
                        alt={img.name}
                        className="landing-image-preview-img"
                      />
                      <button className="landing-image-remove-btn" onClick={() => setPendingImages(prev => prev.filter((_, i) => i !== idx))} title="Remove image">&times;</button>
                    </div>
                  ))}
                </div>
                <button className="landing-submit-btn" onClick={handleSubmit} disabled={analysisLoading}>
                  <FaSearch className="submit-icon" size={18} />
                  <span>{analysisLoading ? 'Analyzing...' : 'Submit For Analysis'}</span>
                </button>
              </>
            )}
            {/* Error message */}
            {analysisError && <div className="error-message">{analysisError}</div>}
            {/* Analysis Results Cards - grid layout handled by CSS Grid */}
            <div className="landing-results-cards-container">
              <div className="landing-results-cards-scroll">
                {/* Centered badge in the grid, spanning both columns */}
                {/* Removed image-count-badge from here */}
               
                {pagedResults.map((result, idx) => (
                  <div className={`landing-results-card${!result.result_image ? ' no-image' : ''}`} key={idx}>
                    {/* Only render image section if result_image exists */}
                    {result.result_image && (
                      <div className="landing-results-image" style={{ cursor: 'zoom-in' }} onClick={() => setZoomedImageIndex(resultsPage * CARDS_PER_PAGE + idx)}>
                        <img src={result.result_image} alt={result.filename} className="landing-results-img" />
                        </div>
                      )}
                    <div className="landing-results-info">
                      <div className="landing-results-title">Analysis Results</div>
                      <div className="landing-results-field">
                        <span className="landing-results-label">Image Name</span>
                        <span className="landing-results-value image-name">{result.filename}</span>
                      </div>
                      <div className="landing-results-field">
                        <span className="landing-results-label">Total Lesions</span>
                        <span className={`landing-results-value ${result.lesion_count <= 5 ? 'lesion-green' : 'lesion-red'}`}>{result.lesion_count}</span>
                      </div>
                      <div className="landing-results-field">
                        <span className="landing-results-label">Necrosis Percentage</span>
                        <span className={`landing-results-value ${Number(result.percentage_necrosis) < 36 ? 'necrosis-green' : Number(result.percentage_necrosis) < 65 ? 'necrosis-orange' : 'necrosis-red'}`}>{Number(result.percentage_necrosis).toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
            </div>
            {totalPages > 1 && (
              <div className="results-page-numbers">
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button
                    key={i}
                    className={`results-page-number${i === resultsPage ? ' active' : ''}`}
                    onClick={() => setResultsPage(i)}
                    disabled={i === resultsPage}
                    style={{
                      margin: '0 6px',
                      padding: '6px 14px',
                      borderRadius: '6px',
                      border: 'none',
                      background: i === resultsPage ? '#066D12' : '#e0e0e0',
                      color: i === resultsPage ? '#fff' : '#222',
                      fontWeight: 700,
                      fontSize: '1rem',
                      cursor: i === resultsPage ? 'default' : 'pointer',
                      boxShadow: i === resultsPage ? '0 2px 8px rgba(6,109,18,0.10)' : 'none',
                      transition: 'background 0.2s, color 0.2s',
                    }}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
            {/* Download All Results Button (inactive for now) */}
            <button className="results-download-btn" onClick={handleDownloadResultsCSV} style={{ margin: '32px auto 0 auto', display: 'block' }}>
              <FaDownload className="download-icon" size={18} />
              <span>Download Results</span>
            </button>
          </div>
        ) : (
          <>
            {/* Image Preview Row (before first analysis) */}
            {selectedImages.length > 0 && !showResults && (
              <>
                <div className={`landing-image-preview-row${isUploaded ? ' landing-image-preview-row-large' : ''}`}>
                  {selectedImages.map((img, idx) => (
                    <div className={`landing-image-preview-item${isUploaded ? ' landing-image-preview-item-large' : ''}`} key={idx}>
                      <img
                        src={URL.createObjectURL(img)}
                        alt={`preview-${idx}`}
                        className="landing-image-preview-img"
                      />
                      <button className="landing-image-remove-btn" onClick={() => handleRemoveImage(idx)} title="Remove image">&times;</button>
                    </div>
                  ))}
                </div>
                <button className="landing-submit-btn" onClick={handleSubmit} disabled={analysisLoading}>
                  <FaSearch className="submit-icon" size={18} />
                  <span>{analysisLoading ? 'Analyzing...' : 'Submit For Analysis'}</span>
                </button>
              </>
            )}
          </>
        )}
        {/* Toggleable Upload Modal */}
        {showUploadContainer && (
          <div className={`landing-upload-modal-wide${(isUploaded || showResults) ? ' landing-upload-modal-wide-uploaded' : ''}${(!isUploaded && !showResults) ? ' landing-upload-modal-centered' : ''}`}>
            <div
              className={`landing-upload-drag-wide${(isUploaded || showResults) ? ' landing-upload-drag-wide-uploaded' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              style={{ position: 'relative' }}
            >
              <FaCloudUploadAlt className="upload-icon" size={40} />
              <div className="upload-text">Drag & Drop Images here (JPEG, PNG, JPG)</div>
              {/* Eye toggle button only when images uploaded or results shown */}
              {(isUploaded || showResults) && (
                <button
                  className="upload-hide-btn"
                  style={{ position: 'absolute', top: 12, right: 18, background: 'none', border: 'none', cursor: 'pointer' }}
                  onClick={() => setShowUploadContainer(false)}
                  title="Hide upload container"
                >
                  <FaEyeSlash size={22} />
                </button>
              )}
            </div>
            <button className="landing-upload-browse-btn" onClick={handleBrowseClick}>
              <FaFolderOpen className="browse-icon" size={22} />
              <span className="browse-btn-text">Browse Files</span>
            </button>
            {/* Hidden file input */}
            <input
              type="file"
              accept="image/jpeg,image/png,image/jpg"
              multiple
              style={{ display: 'none' }}
              ref={fileInputRef}
              onChange={handleFileChange}
            />
          </div>
        )}
        {/* Floating show button when upload container is hidden */}
        {(isUploaded || showResults) && !showUploadContainer && (
          <button
            className="upload-show-btn"
            style={{ position: 'fixed', right: 24, bottom: 24 + 60, zIndex: 110, background: '#fff', border: '1.5px solid #066D12', borderRadius: '50%', width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.10)', cursor: 'pointer' }}
            onClick={() => setShowUploadContainer(true)}
            title="Show upload container"
          >
            <FaEye size={26} color="#066D12" />
          </button>
        )}
      </div>
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-title">Confirm Deletion</div>
            <div className="modal-message">
              Are you sure you want to delete this analysis session? This action cannot be undone.
            </div>
            {deleteError && <div className="modal-error">{deleteError}</div>}
            <div className="modal-actions">
              <button className="modal-btn modal-cancel" onClick={handleCancelDelete}>Cancel</button>
              <button className="modal-btn modal-confirm" onClick={handleConfirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
      {toast.message && (
        <div className={`toast toast-${toast.type}`}>{toast.message}</div>
      )}
    </div>
  );
};

export default LandingPage;