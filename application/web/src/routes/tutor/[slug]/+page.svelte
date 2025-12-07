<!-- <script lang="ts">
	import { page } from '$app/state';
	import { Avatar } from '@ark-ui/svelte/avatar';
</script>

<div class="min-w-screen flex flex-row gap-8 bg-neutral-100 p-16">
	<div class="w-full rounded-2xl bg-white p-6 shadow-lg">
		<div class="flex h-full w-full flex-row gap-8">
			<div class="flex h-full w-1/3 flex-col items-center">
				<h1>id: {page.params.slug}</h1>
				<Avatar.Root>
					<Avatar.Fallback>TN</Avatar.Fallback>
					<Avatar.Image
						src="https://i.pravatar.cc/3000?u=a"
						alt="avatar"
						class="h-96 w-96 rounded-full"
					/>
				</Avatar.Root>
				<h3 class="pt-16 text-3xl">Tutor Name</h3>
				<p class="px-8 pt-8 text-xl text-neutral-500">
					This is an example description for the tutor page. This is text that should be filled in
					by the person who created the tutor account.
				</p>
			</div>
			<div class="flex h-full w-1/3 flex-col items-center">
				<h2 class="text-4xl">Available Appointments</h2>
			</div>
			<div class="flex h-full w-1/3 flex-col items-center">
				<div class="h-1/2 w-full">
					<h2 class="text-4xl">Contact</h2>
					<div class="pt-4">
						<p class="text-xl">
							Email: <a href="mailto:tutoremail@sfsu.edu">tutoremail@sfsu.edu</a>
						</p>
					</div>
				</div>
				<div class="h-1/2 w-full">
					<h2 class="pb-8 text-4xl">Reviews</h2>
					<p class="text-xl">
						<span class="font-bold">Reviewer Name</span>: This was the best tutor ever!
					</p>
					<p class="text-xl">
						<span class="font-bold">Reviewer Name</span>: This was the worst tutor ever!
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
 -->

 <script lang="ts">
	import { page } from '$app/state';

    // Check 
    let isTutor = $state(true); 

    // Single instance of tutor
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
        date: string;
        timeStart: string;
        timeEnd: string;
        tags?: string;
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

    // Pull full tutor info (profile, session, % review)
    async function loadTutorPage () {
        // profile pull 
        try {
            // Pull tutor profile 
			const pResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorId)}`);
			const pData = await pResponse.json();
			profile = pData as Profile;

            // Pull tutor's sessions
            const sResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorId)}/sessions`);
			const sData = await sResponse.json();
			sessions = sData as Session[];

            // Pull tutor's reviews TODO
            const rResponse = await fetch(`/api/tutors/${encodeURIComponent(tutorId)}`);
			const rData = await rResponse.json();
			reviews = rData as Review[];

		} catch (error) {
			console.error('Search failed:', error);
        }
    }

    // Removes session from availability and adds to user session 
    function scheduleSession(sessionId: number) {
        alert(`Session added`);
    }

    loadTutorPage();
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
                    <a href="./review" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">
                        Leave a Review!
                    </a>
                </div>
            </div>
        </div>

        <!--Available tutor sessions col-->
        <div class="w-full p-4 md:w-7/12">
            <h2 class="text-center mb-4 text-4xl underline">Available Tutoring Sessions</h2>
            <!--session card(s)-->
            {#each sessions as session (session.sId)}
                <div class="mx-auto flex flex-col mb-4 rounded-2xl bg-white p-4 drop-shadow-lg md:flex-row">
                    <div class="w-full md:w-9/12">
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
                <a href="./session" class="bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded"> 
                    Add session
                </a>
            </div>
                
            {/if}
        </div>

    </div>
</div>