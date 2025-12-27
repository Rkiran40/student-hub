// API Types

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Legacy auth API (now implemented via backend)
export const authApi = {
  forgotUsername: async (email: string) => {
    const res = await fetch(`${API_URL}/auth/forgot-username`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    return res.json();
  },

  forgotPassword: async (email: string) => {
    const res = await fetch(`${API_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    return res.json();
  },

  resetPassword: async (email: string, otp: string, newPassword: string) => {
    const res = await fetch(`${API_URL}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp, newPassword }),
    });
    return res.json();
  },

  verifyOtp: async (email: string, otp: string) => {
    // stubbed for now
    return { success: true, message: 'Email verified successfully.' };
  },

  changePassword: async (newPassword: string) => {
    const res = await fetch(`${API_URL}/auth/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ newPassword }),
    });
    if (res.status === 401) throw new Error('Not authenticated');
    return res.json();
  },

  resendOtp: async (email: string) => {
    // stubbed
    return { success: true, message: 'Verification email resent.' };
  },
};

export interface User {
  id: string;
  user_id: string;
  username: string | null;
  email: string;
  full_name: string;
  contact_number: string | null;
  college_name: string | null;
  college_id: string | null;
  college_email: string | null;
  status: 'pending' | 'active' | 'suspended';
  created_at: string;
}

export interface DailyUpload {
  id: string;
  user_id: string;
  file_name: string;
  file_url: string;
  file_type: string | null;
  file_size: number | null;
  upload_date: string | null;
  description: string | null;
  status: 'pending' | 'reviewed' | 'approved' | 'rejected';
  admin_feedback: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string | null;
}

// Admin API
export const adminApi = {
  getAllStudents: async (): Promise<User[]> => {
    const res = await fetch(`${API_URL}/admin/students`, { headers: { ...getAuthHeaders() } });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data?.message || 'Failed to fetch students');
    }
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },

  approveStudent: async (profileId: string, username: string): Promise<{ success: boolean; message: string }> => {
    const res = await fetch(`${API_URL}/admin/students/${profileId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ username }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.message || 'Failed to approve student');
    }
    return data;
  },

  suspendStudent: async (profileId: string): Promise<{ success: boolean; message: string }> => {
    const res = await fetch(`${API_URL}/admin/students/${profileId}/suspend`, { 
      method: 'POST', 
      headers: { ...getAuthHeaders() } 
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.message || 'Failed to suspend student');
    }
    return data;
  },

  activateStudent: async (profileId: string): Promise<{ success: boolean; message: string }> => {
    const res = await fetch(`${API_URL}/admin/students/${profileId}/activate`, { 
      method: 'POST', 
      headers: { ...getAuthHeaders() } 
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.message || 'Failed to activate student');
    }
    return data;
  },

  getStudentUploads: async (userId: string): Promise<DailyUpload[]> => {
    const res = await fetch(`${API_URL}/admin/uploads`, { headers: { ...getAuthHeaders() } });
    if (!res.ok) throw new Error('Failed to fetch uploads');
    const all = await res.json();
    return (all || []).filter((u: any) => u.user_id === userId);
  },

  updateUploadStatus: async (
    uploadId: string,
    status: 'reviewed' | 'approved' | 'rejected',
    feedback?: string
  ): Promise<{ success: boolean; message: string }> => {
    const res = await fetch(`${API_URL}/admin/uploads/${uploadId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({ status, feedback }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data?.message || 'Failed to update upload status');
    }
    return data;
  },

  getAllUploads: async (): Promise<(DailyUpload & { student_name: string })[]> => {
    const res = await fetch(`${API_URL}/admin/uploads`, { headers: { ...getAuthHeaders() } });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data?.message || 'Failed to fetch uploads');
    }
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },
};

// Student API
export const studentApi = {
  getUploads: async (): Promise<DailyUpload[]> => {
    const res = await fetch(`${API_URL}/student/uploads`, { headers: { ...getAuthHeaders() } });
    if (res.status === 401) throw new Error('Not authenticated');
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data?.message || 'Failed to fetch uploads');
    }
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  },

  uploadFile: async (file: File, description?: string): Promise<{ success: boolean; message: string; upload?: DailyUpload }> => {
    const form = new FormData();
    form.append('file', file);
    if (description) form.append('description', description);

    const res = await fetch(`${API_URL}/student/uploads`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: form,
    });

    if (res.status === 401) throw new Error('Not authenticated');
    return res.json();
  },

  getProfile: async (): Promise<any> => {
    const res = await fetch(`${API_URL}/student/profile`, { headers: { ...getAuthHeaders() } });
    if (res.status === 401) throw new Error('Not authenticated');
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  updateProfile: async (data: {
    fullName?: string;
    contactNumber?: string;
    collegeName?: string;
    collegeId?: string;
    collegeEmail?: string;
  }): Promise<{ success: boolean; message: string }> => {
    const res = await fetch(`${API_URL}/student/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    });
    if (res.status === 401) throw new Error('Not authenticated');
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },
};
