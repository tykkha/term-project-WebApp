export const API_BASE = '/api';

// Map of course names to tag IDs (based on database Tags table)
export const COURSE_TAG_MAP: { [key: string]: number } = {
	'CSC 101': 1,
	'CSC 210': 1,
	'CSC 215': 2,
	'CSC 220': 3,
	'CSC 600': 4,
	'CSC 415': 5,
	'CSC 413': 5,
	'CSC 256': 6,
	'CSC 230': 7,
	'CSC 648': 4,
	'MATH 226': 8,
	'MATH 227': 9,
	'PHYS 220': 10,
	'PHYS 230': 10,
	'CHEM 115': 11,
	'BIOL 230': 12
};

// Helper function to get tag IDs from course names
export function getCourseTagIds(courses: string[]): number[] {
	return courses.map((course) => COURSE_TAG_MAP[course]).filter((id) => id !== undefined);
}

/* ---------- SEARCH ---------- */

export interface TutorPost {
	pid: number;
	course: string;
	content: string;
	timestamp: string;
}

export interface SearchResult {
	tid: number;
	name: string;
	email: string;
	rating: number;
	profile_tags: string[];
	bio: string | null;
	posts: TutorPost[];
	courses: string[];
}

export async function searchTutors(query: string): Promise<SearchResult[]> {
	const url =
		query && query.trim().length > 0
			? `${API_BASE}/search/${encodeURIComponent(query.trim())}`
			: `${API_BASE}/search`;

	const res = await fetch(url);
	if (!res.ok) {
		let msg = 'Search request failed';
		try {
			const err = await res.json();
			if (err?.detail) msg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(msg);
	}

	return res.json();
}

/* ---------- AUTH & USERS ---------- */

export interface User {
	uid: number;
	firstName: string;
	lastName: string;
	email: string;
	profilePicture?: string | null;
	bio?: string | null;
}

export interface RegisterPayload {
	firstName: string;
	lastName: string;
	email: string;
	password: string;
	phone: string | null;
	studentId: string | null;
	profilePicture?: string | null;
	bio?: string | null;
}

export interface RegisterResponse {
	message: string;
	user: User;
}

export interface LoginResponse {
	message: string;
	user: User;
	sessionID: string;
}

const SESSION_KEY = 'sessionID';
const USER_KEY = 'currentUser';

export function saveSession(sessionID: string, user: User) {
	if (typeof window === 'undefined') return;
	localStorage.setItem(SESSION_KEY, sessionID);
	localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
	if (typeof window === 'undefined') return;
	localStorage.removeItem(SESSION_KEY);
	localStorage.removeItem(USER_KEY);
}

export function getSessionID(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem(SESSION_KEY);
}

export function getCurrentUser(): User | null {
	if (typeof window === 'undefined') return null;
	const raw = localStorage.getItem(USER_KEY);
	return raw ? (JSON.parse(raw) as User) : null;
}

export async function registerUser(payload: RegisterPayload): Promise<RegisterResponse> {
	const res = await fetch(`${API_BASE}/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	if (!res.ok) {
		let errMsg = 'Registration failed';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}

	return res.json();
}

export async function loginUser(email: string, password: string): Promise<LoginResponse> {
	const res = await fetch(`${API_BASE}/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password })
	});

	if (!res.ok) {
		let errMsg = 'Login failed';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}

	const data = (await res.json()) as LoginResponse;
	saveSession(data.sessionID, data.user);
	return data;
}

export async function logoutUser(): Promise<void> {
	const sessionID = getSessionID();
	if (!sessionID) {
		clearSession();
		return;
	}

	try {
		await fetch(`${API_BASE}/logout`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ sessionID })
		});
	} catch {
		// ignore network errors on logout
	}

	clearSession();
}

/* ---------- AUTH FETCH WRAPPER ---------- */

export async function authFetch(input: string, init: RequestInit = {}) {
	const sessionID = getSessionID();
	const headers = new Headers(init.headers || {});

	if (sessionID) {
		headers.set('Authorization', `Bearer ${sessionID}`);
	}

	return fetch(input, {
		...init,
		headers
	});
}

/* ---------- TAGS / COURSES ---------- */

export interface Tag {
	id: number;
	name: string;
}

export async function getTags(): Promise<Tag[]> {
	const res = await fetch(`${API_BASE}/tags`);
	if (!res.ok) {
		throw new Error('Failed to load course tags');
	}
	return res.json();
}

/* ---------- SESSIONS ---------- */

export interface Session {
	sid: number;
	student: { uid: number; name: string };
	tutor: { tid: number; name: string };
	course: string;
	day: string;
	time: number;
	started: string | null;
	concluded: string | null;
}

export interface CreateSessionPayload {
	uid: number;
	tid: number;
	tagsID: number;
	day: string;
	time: number;
}

export async function createSession(payload: CreateSessionPayload): Promise<Session> {
	const res = await authFetch(`${API_BASE}/sessions`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	if (!res.ok) {
		let errMsg = 'Failed to create session';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}

	return res.json();
}

export async function getUserSessions(uid: number): Promise<Session[]> {
	const res = await authFetch(`${API_BASE}/users/${uid}/sessions`);
	if (!res.ok) {
		return [];
	}
	return res.json();
}

/* ---------- TUTORS ---------- */

export interface TutorResponse {
	tid: number;
	uid: number;
	rating: number;
	status: string;
	verificationStatus: string;
}

// Create tutor profile (requires authentication)
export async function createTutorProfile(uid: number, sessionID: string): Promise<TutorResponse> {
	const response = await fetch(`${API_BASE}/tutors`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${sessionID}`
		},
		body: JSON.stringify({
			uid: uid,
			rating: 0.0,
			status: 'available'
		})
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to create tutor profile');
	}

	return response.json();
}

// Add tags/subjects to tutor profile
export async function addTutorTags(
	tid: number,
	tagIds: number[],
	sessionID: string
): Promise<void> {
	const response = await fetch(`${API_BASE}/tutors/${tid}/tags`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${sessionID}`
		},
		body: JSON.stringify({ tagIds })
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to add tutor tags');
	}
}

export async function getTopTutors(): Promise<any[]> {
	const res = await fetch(`${API_BASE}/tutors/top`);
	if (!res.ok) {
		return [];
	}
	return res.json();
}

/* ---------- USER PROFILE UPDATES ---------- */

export interface UpdateUserPayload {
	firstName?: string;
	lastName?: string;
	profilePicture?: string;
	bio?: string;
}

export async function updateUser(uid: number, payload: UpdateUserPayload): Promise<void> {
	const res = await authFetch(`${API_BASE}/users/${uid}`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	if (!res.ok) {
		let errMsg = 'Failed to update profile';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}
}

export async function uploadProfilePicture(uid: number, file: File): Promise<string> {
	const formData = new FormData();
	formData.append('file', file);

	const res = await authFetch(`${API_BASE}/users/${uid}/profile-picture`, {
		method: 'POST',
		body: formData
	});

	if (!res.ok) {
		let errMsg = 'Failed to upload profile picture';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}

	const data = await res.json();
	return data.profilePicture;
}

export interface AvailabilitySlot {
	availabilityID?: number;
	tid: number;
	day: string;
	startTime: number;
	endTime: number;
	isActive?: boolean;
}

export async function getTutorAvailability(tid: number): Promise<AvailabilitySlot[]> {
	const res = await authFetch(`${API_BASE}/tutors/${tid}/availability`);
	if (!res.ok) {
		throw new Error('Failed to fetch availability');
	}
	return res.json();
}

export async function addAvailabilitySlot(
	tid: number,
	day: string,
	startTime: number,
	endTime: number
): Promise<AvailabilitySlot> {
	const res = await authFetch(`${API_BASE}/tutors/${tid}/availability`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ day, startTime, endTime })
	});

	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err?.detail || 'Failed to add availability');
	}

	return res.json();
}

export async function setBulkAvailability(
	tid: number,
	slots: Omit<AvailabilitySlot, 'availabilityID' | 'tid' | 'isActive'>[]
): Promise<void> {
	const res = await authFetch(`${API_BASE}/tutors/${tid}/availability`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ slots })
	});

	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err?.detail || 'Failed to update availability');
	}
}

export async function deleteAvailabilitySlot(tid: number, availabilityID: number): Promise<void> {
	const res = await authFetch(`${API_BASE}/tutors/${tid}/availability/${availabilityID}`, {
		method: 'DELETE'
	});

	if (!res.ok) {
		throw new Error('Failed to delete availability slot');
	}
}

export async function checkTutorAvailability(
	tid: number,
	day: string,
	time: number
): Promise<boolean> {
	const res = await authFetch(
		`${API_BASE}/tutors/${tid}/availability/check?day=${day}&time=${time}`
	);
	if (!res.ok) {
		return false;
	}
	const data = await res.json();
	return data.available;
}

export async function getAvailableTimesForDay(tid: number, day: string): Promise<number[]> {
	const res = await authFetch(`${API_BASE}/tutors/${tid}/availability/day/${day}`);
	if (!res.ok) {
		return [];
	}
	const data = await res.json();
	return data.availableTimes || [];
}

/* ---------- POSTS ---------- */

export interface Post {
    pid: number;
    tid: number;
    tagsID: number;
    content: string;
    timestamp?: string; 
}

export interface CreatePostPayload {
    tid: number;
    tagsID: number;
    content: string;
}

// Creates a new post for a tutor profile
export async function createPost(payload: CreatePostPayload): Promise<Post> {
    const res = await authFetch(`${API_BASE}/posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        let errMsg = 'Failed to create post';
        try {
            const err = await res.json();
            if (err?.detail) errMsg = err.detail;
        } catch {
            /* ignore */
        }
        throw new Error(errMsg);
    }

    return res.json();
}

export async function getPosts(tid: number): Promise<Post[]> {
    const res = await fetch(`${API_BASE}/tutors/${tid}/posts`);

    if (!res.ok) {
        // Log the error and return an empty array or throw an error
        console.error(`Failed to fetch posts for tutor ${tid}`);
        return [];
    }

    return res.json();
}

/* ---------- REVIEWS ---------- */

export interface Review {
    rid: number;
	tid: number;
    uid: number;
	sid: number; 
    rating: number;
}

export interface CreateReviewPayload {
	tid: number;
    uid: number;
    sid: number;
    rating: number; 
}

export async function createReview(payload: CreateReviewPayload): Promise<Review> {
    const res = await authFetch(`${API_BASE}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        let errMsg = 'Failed to submit review';
        try {
            const err = await res.json();
            if (err?.detail) errMsg = err.detail;
        } catch {
            /* ignore */
        }
        throw new Error(errMsg);
    }

    return res.json();
}

/* ---------- MESSAGES ---------- */

export interface Message {
	mid: number;
	senderUID: number;
	receiverUID: number;
	senderName: string;
	content: string;
	timestamp: string;
}

export interface Conversation {
	otherUID: number;
	otherName: string;
	lastMessage: string;
	lastMessageTime: string;
}

export interface SendMessagePayload {
	senderUID: number;
	receiverUID: number;
	content: string;
}

// Check if two users can message each other
export async function canMessage(uid1: number, uid2: number): Promise<boolean> {
	const res = await authFetch(`${API_BASE}/messages/can-message/${uid1}/${uid2}`);
	if (!res.ok) {
		return false;
	}
	const data = await res.json();
	return data.allowed;
}

// Send a message
export async function sendMessage(payload: SendMessagePayload): Promise<Message> {
	const res = await authFetch(`${API_BASE}/messages`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	if (!res.ok) {
		let errMsg = 'Failed to send message';
		try {
			const err = await res.json();
			if (err?.detail) errMsg = err.detail;
		} catch {
			/* ignore */
		}
		throw new Error(errMsg);
	}

	return res.json();
}

// Get conversation between two users
export async function getConversation(
	uid1: number,
	uid2: number,
	limit: number = 50,
	offset: number = 0
): Promise<Message[]> {
	const res = await authFetch(
		`${API_BASE}/messages/${uid1}/${uid2}?limit=${limit}&offset=${offset}`
	);
	if (!res.ok) {
		throw new Error('Failed to load conversation');
	}
	return res.json();
}

// Get recent conversations for a user
export async function getRecentConversations(uid: number, limit: number = 20): Promise<Conversation[]> {
	const res = await authFetch(`${API_BASE}/users/${uid}/conversations?limit=${limit}`);
	if (!res.ok) {
		throw new Error('Failed to load conversations');
	}
	return res.json();
}

// WebSocket connection helper
export function createWebSocket(userId: number, token: string): WebSocket {
	const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
	
	let wsUrl: string;
	if (isDevelopment) {
		const backendPort = '8001';
		wsUrl = `ws://localhost:${backendPort}/api/ws/${userId}?token=${token}`;
	} else {
		// In production, use same host with wss protocol
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		wsUrl = `${protocol}//${window.location.host}/api/ws/${userId}?token=${token}`;
	}
	
	console.log('Connecting to WebSocket:', wsUrl);
	return new WebSocket(wsUrl);
}