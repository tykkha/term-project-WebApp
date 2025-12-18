<script lang="ts">
	import { goto } from '$app/navigation';
    import { page } from '$app/state';
    import {
        authFetch, 
        getCurrentUser,
        type User,
        type Tag,
        createPost,
        getPosts,
        deletePost,
        type Post,
        type CreatePostPayload,
        type TutorResponse,
        createReview,
        type CreateReviewPayload,
        getUserSessions, 
        type Session,
        getTutorAvailability,
		type AvailabilitySlot
    } from '$lib/api';
    import { onMount } from 'svelte';

    // Pull tutor ID from URL
    const tutorId = page.params.slug;
    const tutorIdNum = Number(tutorId);

    // Check current user and tutor status
    let isTutor = $state(false); 
    let uData = $state<User | null>(getCurrentUser());
    let tData = $state<TutorResponse>();
    
    // Single instance of tutor profile
    interface Profile {
        photo: string;
        name: string;
        email: string;
        expertise: Tag[]; 
        rating?: number;
        bio?: string;
    }

    // Stores full tutor info 
    let profile = $state<Profile>({
        photo: '',
        name: '',
        email: '',
        expertise: [],
        bio: '',
    });
    let tutorSessions = $state([] as AvailabilitySlot[]);
    let tutorPosts = $state([] as Post[]); 
    
    //  Post Form  
    let showPostForm = $state(false);
    let isLoadingTags = $state(false);
    let postForm = $state<Omit<CreatePostPayload, 'tid'>>({
        tagsID: 0, 
        content: ''
    });

    // Review Form 
    let showReviewForm = $state(false);
    let reviewErrorMessage = $state('');
    let reviewSuccessMessage = $state('');
    let isReviewSubmitting = $state(false);
    let userReviewableSessions = $state<Session[]>([]); // Sessions the user can review
    let isLoadingReviewableSessions = $state(false);

    // Form state for creating a new review
    let reviewForm = $state<CreateReviewPayload>({
        tid: tutorIdNum,
        uid: 0, // Will be set in loadCurrUserData
        sid: 0, // Session ID selected by user
        rating: 1, 
    });

    // Helper to format session info for the dropdown
    function formatSession(session: Session): string {
        const date = session.day;
        const time = `${session.time}:00`; 
        return `${session.course} on ${date} at ${time}`;
    }
    
    // Submission state and messages (shared for Post & Review)
    let isSubmitting = $state(false);
    let errorMessage = $state('');
    let successMessage = $state('');

    // Pull full tutor info (profile, session, & review)
    async function loadTutorPage () {
        // Full profile pull 
        try {
            // Pull tutor profile 
            const pResponse = await authFetch(`/api/tutors/${tutorIdNum}`);
            const pData = await pResponse.json();
            console.log('Tutor Profile Data:', pData);
            profile = pData as Profile;

            // Pull tutor's available sessions
            const availableSessions = await getTutorAvailability(tutorIdNum);
            tutorSessions = availableSessions;
            console.log('Tutor Availability Sessions Data:', tutorSessions);

            await loadTutorPosts();
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    // Check if current user is the page's tutor, then load tutor data
    async function loadCurrUserData() {
        if (uData) {
            console.log('Current User Data:', uData);
            reviewForm.uid = uData.uid; // Set user ID for review form
            const tutorRes = await fetch(`/api/tutors/by-user/${uData.uid}`);
            tData = await tutorRes.json();
            console.log('Current Tutor Data:', tData);
            if (tData && tData?.tid == tutorIdNum) {
                console.log('User is the tutor for this page');
                isTutor = true;
            } else {
                isTutor = false;
            } 
        }
    }
    
    function openPostForm() {
        showPostForm = true;
        errorMessage = '';
        successMessage = '';
        postForm.content = '';
        if (profile.expertise.length > 0 && postForm.tagsID === 0) {
            postForm.tagsID = profile.expertise[0].id;
        }
    }

    function closePostForm() {
        showPostForm = false;
    }

    async function loadTutorPosts() {
        try {
            const posts = await getPosts(tutorIdNum);
            tutorPosts = posts;
            console.log('Tutor Posts Data:', tutorPosts);
        } catch (error) {
            console.error('Failed to load tutor posts:', error);
        }
    }

       async function handleDeletePost(pid: number) {
        if (!confirm('Are you sure you want to delete this post?')) {
            return;
        }

        try {
            await deletePost(pid);
            // Immediately update the list
            tutorPosts = tutorPosts.filter(post => post.pid !== pid);
            alert('Post deleted successfully!');
        } catch (err) {
            console.error('Failed to delete post:', err);
            alert('Failed to delete post. Please try again.');
        }
    }

    async function handlePostForm() {
        if (!postForm.content.trim() || postForm.tagsID === 0) {
            errorMessage = 'Please select a course and enter content.';
            return;
        }

        isSubmitting = true;
        errorMessage = '';
        successMessage = '';

        try {
            const payload: CreatePostPayload = {
                tid: tData.tid,
                tagsID: postForm.tagsID,
                content: postForm.content.trim()
            };
            await createPost(payload);

            await loadTutorPosts(); 
            successMessage = 'Post created successfully!';
            setTimeout(() => {
                closePostForm();
            }, 1500);

        } catch (err: any) {
            errorMessage = err.message || 'An unexpected error occurred during posting.';
        } finally {
            isSubmitting = false;
        }
    }

    // Check if user can review tutor
    async function loadReviewableSessions() {
        if (!uData || isTutor) return; 

        isLoadingReviewableSessions = true;
        reviewErrorMessage = '';
        userReviewableSessions = [];

        try {
            const allSessions = await getUserSessions(uData.uid);
            const concludedSessionsWithCurrentTutor = allSessions.filter(s => 
                 s.tutor.tid === tutorIdNum && s.concluded !== null
            );
            userReviewableSessions = concludedSessionsWithCurrentTutor;

            if (userReviewableSessions.length === 0) {
                reviewErrorMessage = "You have no concluded sessions with this tutor to review.";
            } else {
                reviewForm.sid = userReviewableSessions[0].sid; // Default to the first session
            }

        } catch (err) {
            console.error('Failed to load reviewable sessions:', err);
            reviewErrorMessage = 'Failed to load your past sessions. Please try again.';
        } finally {
            isLoadingReviewableSessions = false;
        }
    }

    function openReviewForm() {
        if (!uData) {
            goto('/login');
            return;
        }
        if (isTutor) {
            alert('Tutors cannot review themselves.');
            return;
        }
        
        showReviewForm = true;
        reviewErrorMessage = '';
        reviewSuccessMessage = '';
        reviewForm.rating = 1;
        reviewForm.sid = 0;
        loadReviewableSessions();
    }

    function closeReviewForm() {
        showReviewForm = false;
    }

    async function handleReviewForm() {
        if (reviewForm.sid === 0 || reviewForm.rating < 1 || reviewForm.rating > 5) {
            reviewErrorMessage = 'Please select a session and provide a valid rating (1-5).';
            return;
        }

        isReviewSubmitting = true;
        reviewErrorMessage = '';
        reviewSuccessMessage = '';

        try {
            const payload = {
                tid: tutorIdNum,
                uid: reviewForm.uid,
                sid: reviewForm.sid,
                rating: reviewForm.rating
            };
            await createReview(payload);

            reviewSuccessMessage = 'Review submitted successfully! Thank you.';
            setTimeout(() => {
                closeReviewForm();
            }, 1500);

        } catch (err: any) {
            console.error('Review submission error:', err);
            reviewErrorMessage = err.message || 'An unexpected error occurred during review submission.';
        } finally {
            isReviewSubmitting = false;
        }
    }
    
    onMount(() => {
        if (tutorIdNum == null || isNaN(tutorIdNum)) {
            goto('/search');  
            return;
        }
        loadCurrUserData();
        loadTutorPage();
    });
</script>

<!-- Tutor Profile Page Layout -->
<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="mx-auto flex flex-col p-8 md:flex-row">

        <!-- Left Column: Tutor Profile & Actions -->
        <div class="w-full p-4 md:w-5/12">
            <div class="mb-8 w-full min-h-64 rounded-2xl bg-white drop-shadow-lg transition duration-300 hover:scale-[1.02] hover:drop-shadow-2xl aspect-square">
                <img src={profile.photo} alt="{profile.name} Profile Photo" class="w-full h-auto rounded-xl">
            </div>

            <div class="mb-8 w-full rounded-2xl bg-white p-4 drop-shadow-lg">
               <div class="flex justify-between items-baseline">
                    <div class="w-1/9"></div> 
                    <h2 class="text-3xl underline text-center w-7/9">{profile.name}</h2>
                    <div class="w-1/9">
                        <h2 class="text-lg text-center rounded-full bg-green-100 text-green-700">
                        {profile.rating ? profile.rating.toFixed(1) : '0.0'}
                        </h2>
                    </div> 
                </div>
                <p class="text-lg text-center">{profile.email}</p>
                <div class="flex flex-wrap justify-center gap-2">
                    {#each profile.expertise as tag}
                        <span class="bg-[#231161] text-white text-sm px-2 py-1 rounded shadow-md">
                            {tag.name}
                        </span>
                    {/each}
                </div>
                <p class="p-3 text-base">{profile.bio}</p>
            </div>

            <div class="flex justify-center">
                <button
                    onclick={openReviewForm}
                    class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                    Leave a Review!
                </button>
            </div>
        </div>

        <!-- Right Column: Available Tutoring Sessions -->
        <div class="w-full p-4 md:w-7/12">
            <div class="mb-8 w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="text-center mb-4 text-4xl underline">Available Tutoring Sessions</h2>

                <!--Available Tutoring Sessions-->
                {#if tutorSessions.length === 0}
                    <p class="text-center text-gray-500 italic">
                        This tutor has no available sessions at the moment.
                    </p>
                {:else}
                    <div class="space-y-4">
                        {#each tutorSessions as session (session.availabilityID)}
                            <div class="rounded-lg border border-gray-200 bg-white p-4 shadow-md">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="text-lg font-semibold text-gray-800">
                                            {session.day}
                                        </h3>
                                        <p class="text-gray-600">
                                            Time: {session.startTime}:00 - {session.endTime}:00
                                        </p>
                                    </div>
                                    <div>
                                        {#if session.isActive}
                                            <span class="text-sm px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                                                Active
                                            </span>
                                        {:else}
                                            <span class="text-sm px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-medium">
                                                Inactive
                                            </span>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}

                {#if isTutor}
                    <div class="flex justify-center mt-4">
                        <a href="./{tutorId}/session" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"> 
                            Add session
                        </a>
                    </div>
                {/if}
            </div>
            <div>
                <div class="mb-8 w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                    <h2 class="text-center mb-4 text-4xl underline">Tutor Posts</h2>
                    <div class="space-y-4">
                        {#if tutorPosts.length === 0}
                            <p class="text-center text-gray-500 italic">
                                This tutor has not created any posts yet.
                            </p>
                        {:else}
                            {#each tutorPosts as post (post.pid)}
                                <div class="rounded-lg border border-gray-200 bg-white p-4 shadow-md">
                                    <div class="flex justify-between items-start mb-2">
                                        <span class="text-sm px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 font-medium">
                                            {profile.expertise.find(t => t.id === post.tagsID)?.name || 'General'}
                                        </span>
                                        
                                        {#if post.timestamp}
                                            <span class="text-xs text-gray-500">
                                                Posted: {new Date(post.timestamp).toLocaleDateString()}
                                            </span>
                                        {/if}
                                    </div>

                                    <p class="text-gray-800 whitespace-pre-wrap">
                                        {post.content}
                                    </p>

                                    {#if isTutor}
                                        <div class="mt-3 flex justify-end">
                                            <button
                                                onclick={() => handleDeletePost(post.pid)}
                                                class="text-xs text-red-600 hover:text-red-800 transition-colors"
                                            >
                                                Delete Post
                                            </button>
                                        </div>
                                    {/if}
                                </div>
                            {/each}
                        {/if}

                        {#if isTutor}
                            <div class="flex justify-center mb-4">
                                <button
                                    onclick={openPostForm}
                                    disabled={isLoadingTags || profile.expertise.length === 0}
                                    class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {isLoadingTags ? 'Loading Courses...' : 'Create New Post'}
                                </button>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{#if showPostForm}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <div class="mb-4 flex items-center justify-between border-b pb-3">
                <h3 class="text-xl font-bold text-gray-800">Create New Tutor Post</h3>
            </div>

            <form onsubmit={handlePostForm} class="space-y-4">
                <div>
                    <label for="post-course" class="mb-1 block text-sm font-medium text-gray-700"
                        >Select Course</label
                    >
                    <select
                        id="post-course"
                        bind:value={postForm.tagsID}
                        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-700 focus:border-[#231161] focus:ring-[#231161]"
                        disabled={isLoadingTags || isSubmitting}
                    >
                        {#each profile.expertise as tags}
                            <option value={tags.id}>{tags.name}</option>
                        {/each}
                    </select>
                </div>

                <div>
                    <label for="post-content" class="mb-1 block text-sm font-medium text-gray-700"
                        >Post Content</label
                    >
                    <textarea
                        id="post-content"
                        bind:value={postForm.content}
                        rows="4"
                        placeholder="Give a brief description of your tutoring services, availability, or any special offers..."
                        class="w-full rounded-lg border border-gray-300 p-3 text-gray-700 focus:border-[#231161] focus:ring-[#231161]"
                        disabled={isSubmitting}
                    ></textarea>
                </div>

                {#if errorMessage}
                    <p class="text-sm text-red-600">{errorMessage}</p>
                {/if}
                {#if successMessage}
                    <p class="text-sm text-green-600">{successMessage}</p>
                {/if}

                <div class="flex justify-end space-x-3 pt-2">
                    <button
                        type="button"
                        onclick={closePostForm}
                        disabled={isSubmitting}
                        class="rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-300 disabled:opacity-50"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={isSubmitting || postForm.tagsID === 0 || !postForm.content.trim()}
                        class="rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
                    >
                        {isSubmitting ? 'Posting...' : 'Post'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}


{#if showReviewForm}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <div class="mb-4 flex items-center justify-between border-b pb-3">
                <h3 class="text-xl font-bold text-gray-800">Leave a Review for {profile.name}</h3>
            </div>

            <form onsubmit={handleReviewForm} class="space-y-4">
                <div>
                    <label for="review-session" class="mb-1 block text-sm font-medium text-gray-700"
                        >Select Completed Session to Review</label
                    >
                    {#if isLoadingReviewableSessions}
                        <p class="text-sm text-gray-500">Loading your past sessions...</p>
                    {:else if userReviewableSessions.length === 0}
                        <p class="text-sm text-red-600">You must complete a session with this tutor before leaving a review.</p>
                    {:else}
                        <select
                            id="review-session"
                            bind:value={reviewForm.sid}
                            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-700 focus:border-[#231161] focus:ring-[#231161]"
                            disabled={isReviewSubmitting}
                        >
                            {#each userReviewableSessions as session}
                                <option value={session.sid}>{formatSession(session)}</option>
                            {/each}
                        </select>
                    {/if}
                </div>

                <div>
                    <label for="review-rating" class="mb-1 block text-sm font-medium text-gray-700"
                        >Rating (1-5 Stars)</label
                    >
                    <input
                        id="review-rating"
                        type="number"
                        min="1"
                        max="5"
                        bind:value={reviewForm.rating}
                        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-700 focus:border-[#231161] focus:ring-[#231161]"
                        disabled={isReviewSubmitting || userReviewableSessions.length === 0}
                    />
                </div>

                {#if reviewErrorMessage}
                    <p class="text-sm text-red-600">{reviewErrorMessage}</p>
                {/if}
                {#if reviewSuccessMessage}
                    <p class="text-sm text-green-600">{reviewSuccessMessage}</p>
                {/if}

                <div class="flex justify-end space-x-3 pt-2">
                    <button
                        type="button"
                        onclick={closeReviewForm}
                        disabled={isReviewSubmitting}
                        class="rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-300 disabled:opacity-50"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={isReviewSubmitting || userReviewableSessions.length === 0}
                        class="rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
                    >
                        {isReviewSubmitting ? 'Submitting...' : 'Submit Review'}
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}