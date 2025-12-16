<script lang="ts">
    import { page } from '$app/state';
    import {parseDate} from '@ark-ui/svelte/date-picker';

    // time 
    const currDay = new Date();
    const date = currDay.toISOString().split('T')[0];
    
    // Review variables 
    let errorMessage = $state('')
    
    // The main variable to submit (the tags the user selected)
    let selectedTags = $state<string[]>([]);    

    // Input for the current search text
    let tagSearchInput = $state('');

    // Temp tags
    const availableTags = [
        'CSC645', 'CSC413', 'CSC648', 'CSC220', 
        'ENGL101', 'MATH300', 'PHYS150', 'BIOL199',
    ];

    const tutorId = page.params.slug;
    let reviewData = $state({
        tId: tutorId,
        rating: 0,
        feedback: '',
        selectedTags: [] as string[]
    });

    // --- Tag Management Functions ---
     let filteredTags = $derived(
        tagSearchInput 
            ? availableTags.filter(tag => 
                  // 1. Tag is NOT already selected
                  !selectedTags.includes(tag) && 
                  // 2. Tag matches the search input
                  tag.toLowerCase().includes(tagSearchInput.toLowerCase())
              )
            : []
    );
        
    function addTag(tag: string) {
        if (!selectedTags.includes(tag)) {
            selectedTags = [...selectedTags, tag];
        }
        tagSearchInput = ''; 
    }

    function removeTag(tagToRemove: string) {
        selectedTags = selectedTags.filter(tag => tag !== tagToRemove);
    }
    
    function isRatingValid (rating: number) : boolean {
        errorMessage = errorMessage + 'Rating not between 1.0 - 5.0.\n';
        return (!isNaN(rating) && (rating) >= 1.0 && (rating) <= 5.0);
    } 

    function isFeedbackValid (feedback: string) : boolean {
        errorMessage = errorMessage + 'Feedback exceeds 200 characters\n';
        return (feedback.length <= 200);
    }

    // Function to handle form submission
    async function handleSubmit() {
        if (isRatingValid(reviewData.rating) || isFeedbackValid(reviewData.feedback)) {
            return;
        }

        console.log("Submitting Review Data:", reviewData);
        try {
            // const response = await fetch ('reviews/', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify(reviewData),
            // });
            
        } catch (error) {
            console.error('Error submitting review:', error);
            errorMessage = 'Failed to submit review. Please try again later.';
        }
    }
        
</script>

<!--Review page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="p-4">
        <a href="/tutor/{tutorId}" class="hover:underline">← Back to Tutor</a>
    </div>
	<div class="flex gap-8 p-8 justify-center">
        <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-6/12">
            <h2 class="text-3xl underline">Write your Review</h2>
            <form onsubmit={handleSubmit}>
                <div class="flex-col">
                    <!--Should be checked to be between 1.0-5.0-->
                    <label for="rating" class="block text-xl">Rating</label>
                    <input type="number" bind:value={reviewData.rating} placeholder="1.0 - 5.0" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg">
                    {#if !isRatingValid}
                        <p class="text-sm text-red-500">Rating is not between 1.0 - 5.0</p>
                    {/if}

                    <!--Tags (courses)-->
                    <div>
                        <label for="" class="block text-xl">Tags (Courses)</label>
                        <div class="relative">
                            <input 
                                type="text" 
                                bind:value={tagSearchInput} 
                                placeholder="Search courses (e.g., CSC645)" 
                                class="w-full p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg"
                            >
                            
                            {#if filteredTags.length > 0}
                                <div class="absolute z-10 w-full bg-white border border-gray-300 rounded-lg shadow-lg mt-1">
                                    {#each filteredTags as tag (tag)}
                                        <button 
                                            type="button"
                                            onclick={() => addTag(tag)}
                                            class="block w-full text-left p-2 hover:bg-neutral-100"
                                        >
                                            {tag}
                                        </button>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                         <div class="flex flex-wrap gap-2 my-2">
                            {#each selectedTags as tag (tag)}
                                <button 
                                    type="button"
                                    onclick={() => removeTag(tag)}
                                    class="flex items-center bg-[#231161] hover:bg-[#2d1982] text-white text-base px-3 py-1 rounded-full"
                                >
                                    {tag}
                                    <span class="ml-1 font-bold">x</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                    
                    <!--Character limit ~200?-->
                    <label for="description" class="block text-xl">Feedback</label>
                    <textarea rows="5" bind:value={reviewData.feedback} placeholder="Share your experience (200 character limit)" class="w-full p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg"></textarea>         
                    <p class="text-base">{reviewData.feedback.length} / 200</p>
                     {#if !isFeedbackValid}
                        <p class="text-sm text-red-500">Feedback exceeds the 200-character limit.</p>
                    {/if}
                    <button type="submit" class="block mx-auto bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>

