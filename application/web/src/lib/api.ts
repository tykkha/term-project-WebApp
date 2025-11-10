export const API_BASE = '/api'; // nginx will proxy this to 127.0.0.1:8000

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
	const response = await fetch(`/api/v1/search/${encodeURIComponent(query)}`);
	if (!response.ok) {
		throw new Error('Search request failed');
	}
	return response.json();
}
