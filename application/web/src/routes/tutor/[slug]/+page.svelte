 <script lang="ts">
	import { page } from '$app/state';
    import {
		getCurrentUser,
		type User,
        getTags,
        type Tag,
        createPost,
        type CreatePostPayload,
		type TutorResponse,
    } from '$lib/api';
    import { onMount } from 'svelte';

    // Check current user and tutor status
    let isTutor = $state(false); 
    let uData = $state<User | null>(getCurrentUser());
    let tData = $state<TutorResponse>();

    // Single instance of tutor profile
    interface Profile {
        photo: string;
        name: string;
        email: string;
        tags: string[]; 
        bio: string;
    }

    // Should be an array to hold tutor's posted sessions
    interface Session {
        sId: number;
        tId: number;
        course: string;
        date: string;
        timeStart: string;
        timeEnd: string;
        location?: string;
    }

    // Should be an array to hold reviews of tutor
    interface Review {
        rId: number;
        user: string;
        rating: number;
        feedback: string;
        date: Date;
    }
    
    // Stores full tutor info 
    let profile = $state<Profile>({
        photo: '',
        name: '',
        email: '',
        tags: [],
        bio: ''
    });
    let sessions = $state([] as Session[]);
    let reviews = $state([] as Review[])

    // Temp id to pull data
    const tutorId = page.params.slug;
    const tutorIdNum = Number(tutorId);

    // Pull full tutor info (profile, session, % review)
    async function loadTutorPage () {
        // profile pull 
        try {
            // Pull tutor profile 
			const pResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorIdNum)}`);
			const pData = await pResponse.json();
			profile = pData as Profile;

            // Pull tutor's sessions
            const sResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorIdNum)}/sessions`);
			const sData = await sResponse.json();
			sessions = sData as Session[];

            // Pull tutor's reviews TODO
            const rResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorIdNum)}`);
			const rData = await rResponse.json();
			reviews = rData as Review[];

		} catch (error) {
			console.error('Search failed:', error);
        }
    }

    // Removes session from availability and adds to user session 
    function scheduleSession(sessionId: number) {
        alert(`Session added`); //TODO
    }

    // Form visibility state and tags for post creation
    let showPostForm = $state(false);
    let tags = $state<Tag[]>([]);
    let isLoadingTags = $state(false);

    // Form state for creating a new post
    let postForm = $state<Omit<CreatePostPayload, 'tid'>>({
        tagsID: 0, 
        content: ''
    });

    // Submission state and messages
    let isSubmitting = $state(false);
    let errorMessage = $state('');
    let successMessage = $state('');

    // Function to load (all; need to change to only tutor listed) available tags/courses
    async function loadTags() {
        isLoadingTags = true;
        try {
            tags = await getTags();
            // Set default selected tag if available
            if (tags.length > 0) {
                postForm.tagsID = tags[0].id;
            }
        } catch (err) {
            console.error('Failed to load tags:', err);
            errorMessage = 'Failed to load courses. Cannot create post.';
        } finally {
            isLoadingTags = false;
        }
    }

    function openPostForm() {
        showPostForm = true;
        errorMessage = '';
        successMessage = '';
        postForm.content = '';
        // Ensure tagsID is set if tags are loaded
        if (tags.length > 0 && postForm.tagsID === 0) {
             postForm.tagsID = tags[0].id;
        }
    }

    function closePostForm() {
        showPostForm = false;
    }

    // Check if current user is the page's tutor, then load tutor data
    async function loadTutorData() {
        if (uData) {
            const tutorRes = await fetch(`/api/tutors/by-user/${encodeURIComponent(uData.uid)}`);
            tData = await tutorRes.json();
            console.log('Tutor Profile Data:', tData);
            if (tData && tData?.tid == tutorIdNum) {
                console.log('User is the tutor for this page');
                isTutor = true;
            } else {
                isTutor = false;
            } 
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

            const newPost = await createPost(payload);

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
    
    onMount(() => {
        loadTags();
        loadTutorData();
        loadTutorPage();
    });
</script>

<!--Tutor page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
	<div class="mx-auto flex flex-col p-8 md:flex-row">

        <!--Tutor profile & reviews col-->
		<div class="w-full p-4 md:w-5/12">
            <!--Tutor photo card-->
			<h1>id: {page.params.slug}</h1>
            <div class="mb-8 w-full rounded-2xl bg-white drop-shadow-lg transition duration-300 hover:scale-[1.02] hover:drop-shadow-2xl">
                <img src={profile.photo} alt="{profile.name} Profile Photo" class="w-full h-auto rounded-xl">
            </div>

            <!--Tutor name, tags, and bio card-->
            <div class="mb-8 w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="text-2xl underline text-center">{profile.name}</h2>
                <p class="text-lg text-center">{profile.email}</p>
                <div class="flex flex-wrap justify-center gap-2">
                    {#each profile.tags as tag}
                        <span class="bg-[#231161] text-white text-sm px-2 py-1 rounded shadow-md">
                            {tag}
                        </span>
                    {/each}
                </div>
                <p class="p-3 text-base">{profile.bio}</p>
            </div>

            <!--Tutor's reviews card-->
            <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg">
                <h2 class="mb-4 text-2xl underline text-center">Reviews</h2>
                {#each reviews as review (review.rId)}
                    <div class="mb-4 rounded-2xl p-3 shadow-sm">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-2xl bg-green-500 px-3 py-1">{review.rating}</span>
                            <span class="font-bold text-xl">{review.user}</span>
                        </div>
						<div class="mb-2 flex flex-wrap gap-2">
							{#each profile.tags as tag}
								<span class="bg-[#231161] text-white text-sm px-2 py-1 rounded shadow-md">
									{tag}
								</span>
							{/each}
						</div>
                        <div>
                            <p class="text-base italic">"{review.feedback}"</p>
                        </div>
						<div class="flex flex-row-reverse items-center mb-2">
                            <span class="font-bold text-xl">{review.date}</span>
                        </div>
                    </div>
                {/each}
                <div class="flex justify-center">
                    <a href="./{tutorId}/review" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">
                        Leave a Review!
                    </a>
                </div>
            </div>

            <!-- TEMP Create Post Button Location -->
            <div>
                <button
                    onclick={openPostForm}
                    disabled={isLoadingTags || tags.length === 0}
                    class="rounded-lg bg-[#231161] px-4 py-2 text-sm font-medium text-white shadow-md transition-colors hover:bg-[#1a0d4a] disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                    {isLoadingTags ? 'Loading Courses...' : 'Create New Post'}
                </button>
            </div>
            
        </div>

        <!--Available tutor sessions col-->
        <div class="w-full p-4 md:w-7/12">
            <h2 class="text-center mb-4 text-4xl underline">Available Tutoring Sessions</h2>
            <!--session card(s)-->
            {#each sessions as session (session.sId)}
                    
                <div class="mx-auto flex flex-col mb-4 rounded-2xl bg-white p-4 drop-shadow-lg md:flex-row">
                    <div class="w-full md:w-9/12">
                        <span class="bg-[#231161] text-white text-sm px-2 py-1 rounded shadow-md">{session.course}</span>
                        <p class="text-lg">Date: {session.date} </p>
                        <p class="text-lg">Time: {session.timeStart} to {session.timeEnd}</p>
                        <p class="text-lg">Location: {session.location}</p>
                    </div>
                    <div class="flex w-full justify-end items-end md:w-3/12">
                        <button 
                            class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"
                            onclick={() => scheduleSession(session.sId)}
                        > <!--TODO add schdule button function-->
                            Schedule
                        </button>
                    </div>
                </div>
            {/each}

            <!--Should only show in tutor view!!!!!-->
            {#if isTutor}
            <div class="flex justify-center">
                <a href="./{tutorId}/session" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"> 
                    Add session
                </a>
            </div>
                
            {/if}
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
                        {#each tags as tag}
                            <option value={tag.id}>{tag.name}</option>
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


