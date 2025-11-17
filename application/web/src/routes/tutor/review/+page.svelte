<script>

</script>

<!--Review page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="p-4">
        <a href="/tutor" class="hover:underline">← Back to Tutor</a>
    </div>
	<div class="flex gap-8 p-8 justify-center">
        <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-6/12">
            <h2 class="text-3xl underline">Write your Review</h2>
            <form action="">
                <div class="flex-col">
                    <!--Should be checked to be between 1.0-5.0-->
                    <label for="rating" class="block text-xl">Rating</label>
                    <input type="text" placeholder="0.0 - 5.0" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg">
                    <!--Character limit ~200?-->
                    <label for="description" class="block text-xl">Feedback</label>
                    <textarea id="" rows="5" placeholder="Share your experience (200 character limit)" class="w-full p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg"></textarea>         
                    <input type="submit" class="block mx-auto bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">
                </div>
            </form>
        </div>
    </div>
</div>