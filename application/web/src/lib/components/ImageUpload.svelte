<script lang="ts">
	import { Upload, X } from '@lucide/svelte';

	interface Props {
		onUpload?: (url: string) => void;
		label?: string;
	}

	let { onUpload, label = 'Upload Image' } = $props();

	let isUploading = $state(false);
	let error = $state('');
	let preview = $state('');

	async function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];

		if (!file) return;

		if (!file.type.startsWith('image/')) {
			error = 'Please select an image file';
			return;
		}

		if (file.size > 5 * 1024 * 1024) {
			error = 'File must be smaller than 5MB';
			return;
		}

		const reader = new FileReader();
		reader.onload = (event) => {
			preview = event.target?.result as string;
		};
		reader.readAsDataURL(file);

		isUploading = true;
		error = '';

		try {
			const formData = new FormData();
			formData.append('file', file);

			const response = await fetch('/api/upload', {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				const data = await response.json();
				throw new Error(data.detail || 'Upload failed');
			}

			const data = await response.json();
			onUpload?.(data.url);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Upload failed';
			preview = '';
		} finally {
			isUploading = false;
			input.value = '';
		}
	}

	function clearPreview() {
		preview = '';
		error = '';
	}
</script>

<div class="flex flex-col gap-4">
	<label class="block">
		<span class="text-sm font-medium text-gray-700">{label}</span>
		<input
			type="file"
			accept="image/*"
			onchange={handleFileSelect}
			disabled={isUploading}
			class="mt-2 block w-full text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-[#231161] file:px-4 file:py-2 file:text-white hover:file:bg-[#2d1982] disabled:file:bg-gray-400"
		/>
	</label>

	{#if error}
		<div class="rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</div>
	{/if}

	{#if preview}
		<div class="relative">
			<img src={preview} alt="preview" class="max-h-48 w-auto rounded-lg" />
			{#if !isUploading}
				<button
					onclick={clearPreview}
					class="absolute right-2 top-2 rounded-full bg-red-500 p-1 text-white hover:bg-red-600"
				>
					<X size={16} />
				</button>
			{/if}
		</div>
	{/if}

	{#if isUploading}
		<div class="text-sm text-gray-600">Uploading...</div>
	{/if}
</div>
