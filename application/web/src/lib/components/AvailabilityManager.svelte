<script lang="ts">
	import { getTutorAvailability, setBulkAvailability, type AvailabilitySlot } from '$lib/api';

	interface Props {
		tutorId: number;
	}

	let { tutorId }: Props = $props();

	const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	const hours = Array.from({ length: 15 }, (_, i) => i + 9); // 9 AM to 11 PM

	let availability = $state<{ [day: string]: Set<number> }>({
		Monday: new Set(),
		Tuesday: new Set(),
		Wednesday: new Set(),
		Thursday: new Set(),
		Friday: new Set(),
		Saturday: new Set(),
		Sunday: new Set()
	});

	let isLoading = $state(false);
	let isSaving = $state(false);
	let error = $state('');
	let success = $state('');

	async function loadAvailability() {
		isLoading = true;
		error = '';

		try {
			const slots = await getTutorAvailability(tutorId);

			// Clear existing
			for (const day of daysOfWeek) {
				availability[day].clear();
			}

			// Populate from API
			for (const slot of slots) {
				for (let hour = slot.startTime; hour < slot.endTime; hour++) {
					availability[slot.day].add(hour);
				}
			}

			// Trigger reactivity
			availability = { ...availability };
		} catch (err: any) {
			error = err.message || 'Failed to load availability';
		} finally {
			isLoading = false;
		}
	}

	function toggleHour(day: string, hour: number) {
		if (availability[day].has(hour)) {
			availability[day].delete(hour);
		} else {
			availability[day].add(hour);
		}
		availability = { ...availability };
	}

	function setDayAvailability(day: string, start: number, end: number) {
		availability[day].clear();
		for (let hour = start; hour <= end; hour++) {
			availability[day].add(hour);
		}
		availability = { ...availability };
	}

	function clearDay(day: string) {
		availability[day].clear();
		availability = { ...availability };
	}

	async function saveAvailability() {
		isSaving = true;
		error = '';
		success = '';

		try {
			const slots: Omit<AvailabilitySlot, 'availabilityID' | 'tid' | 'isActive'>[] = [];

			for (const day of daysOfWeek) {
				const hours = Array.from(availability[day]).sort((a, b) => a - b);

				// Group consecutive hours into slots
				if (hours.length > 0) {
					let startTime = hours[0];
					let endTime = hours[0] + 1;

					for (let i = 1; i < hours.length; i++) {
						if (hours[i] === endTime) {
							endTime++;
						} else {
							slots.push({ day, startTime, endTime });
							startTime = hours[i];
							endTime = hours[i] + 1;
						}
					}

					slots.push({ day, startTime, endTime });
				}
			}

			await setBulkAvailability(tutorId, slots);
			success = 'Availability saved successfully!';

			setTimeout(() => {
				success = '';
			}, 3000);
		} catch (err: any) {
			error = err.message || 'Failed to save availability';
		} finally {
			isSaving = false;
		}
	}

	function formatTime(hour: number): string {
		const period = hour >= 12 ? 'PM' : 'AM';
		const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
		return `${displayHour}:00 ${period}`;
	}

	$effect(() => {
		if (tutorId) {
			loadAvailability();
		}
	});
</script>

<div class="rounded-lg bg-white p-6 shadow">
	<h3 class="mb-4 text-xl font-bold text-gray-800">Manage Availability</h3>

	{#if error}
		<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
			{error}
		</div>
	{/if}

	{#if success}
		<div class="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
			{success}
		</div>
	{/if}

	{#if isLoading}
		<div class="py-8 text-center">
			<div class="animate-pulse text-gray-600">Loading availability...</div>
		</div>
	{:else}
		<div class="mb-4 text-sm text-gray-600">
			Click on time slots to toggle your availability. Selected hours are highlighted in purple.
		</div>

		<div class="space-y-4">
			{#each daysOfWeek as day}
				<div class="rounded-lg border border-gray-200 p-4">
					<div class="mb-3 flex items-center justify-between">
						<h4 class="font-semibold text-gray-800">{day}</h4>
						<div class="flex gap-2">
							<button
								onclick={() => setDayAvailability(day, 9, 17)}
								class="rounded bg-blue-100 px-2 py-1 text-xs text-blue-700 hover:bg-blue-200"
							>
								9 AM - 5 PM
							</button>
							<button
								onclick={() => clearDay(day)}
								class="rounded bg-gray-100 px-2 py-1 text-xs text-gray-700 hover:bg-gray-200"
							>
								Clear
							</button>
						</div>
					</div>

					<div class="flex flex-wrap gap-2">
						{#each hours as hour}
							<button
								onclick={() => toggleHour(day, hour)}
								class="rounded px-3 py-2 text-xs font-medium transition-colors {availability[
									day
								].has(hour)
									? 'bg-[#231161] text-white'
									: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'}"
							>
								{formatTime(hour)}
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>

		<div class="mt-6 flex justify-end">
			<button
				onclick={saveAvailability}
				disabled={isSaving}
				class="rounded-lg bg-[#231161] px-6 py-3 font-medium text-white transition-colors hover:bg-[#1a0d4a] disabled:opacity-50"
			>
				{isSaving ? 'Saving...' : 'Save Availability'}
			</button>
		</div>
	{/if}
</div>
