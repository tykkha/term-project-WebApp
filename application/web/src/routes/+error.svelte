<script lang="ts">
	import { page } from '$app/state';
</script>

<div class="flex h-screen w-screen items-center justify-center bg-white text-black">
	<h2 class="text-center text-4xl font-bold">{page.status} {page.error.message}</h2>
</div>
