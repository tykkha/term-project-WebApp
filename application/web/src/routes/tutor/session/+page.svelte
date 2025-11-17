<script>

</script>

<!--Session page-->
<div class="min-h-screen min-w-screen bg-neutral-100">
    <div class="p-4">
        <a href="/tutor" class="hover:underline">← Back to Tutor</a>
    </div>
	<div class="flex gap-8 p-8 justify-center">
        <div class="w-full rounded-2xl bg-white p-4 drop-shadow-lg md:w-6/12">
            <h2 class="text-3xl underline">Add a tutor session</h2>
            <form id="sessionForm">
                <div class="flex-col">
                    <!--Should check input for possible date-->
                    <label for="date" class="block text-xl">Date</label>
                    <input type="text" placeholder="DD/MM/YYYY" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg" required>
                    <!--Session duration-->                        
                    <label for="time" class="block text-xl">Session time and duration</label>
                    <input type="text" id="" placeholder="start" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg"> to
                    <input type="text" id="" placeholder="end" class="p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg">
                    <!--Optional-->
                    <label for="location" class="block text-xl">Location (Optional)</label>
                    <input type="text" id="" placeholder="In-person location or online meeting" class="w-full p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#231161] focus:border-[#231161] rounded-lg">
                    <input type="submit" class="block mx-auto bg-[#231161] hover:bg-[#2d1982] text-white py-2 px-3 rounded">
                </div>
            </form>
        </div>
    </div>
</div>