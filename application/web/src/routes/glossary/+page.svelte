<script lang="ts">
	import { DatePicker, parseDate } from '@ark-ui/svelte/date-picker';
	import { Field } from '@ark-ui/svelte/field';
	import { Portal } from '@ark-ui/svelte/portal';
	import { CalendarIcon, ChevronLeft, ChevronRight, Search as SearchIcon } from '@lucide/svelte';
	import { onMount } from 'svelte';

	const today = new Date();
	const formatted = today.toISOString().split('T')[0];
	let value = $state([parseDate(formatted)]);

	interface Tutor {
		name: string;
		rating?: number;
		email?: string;
		courses: string[];
		bio?: string;
		posts: { course: string; content: string }[];
	}

	// Search state
	let searchQuery = $state('');
	let searchResults = $state([]) as Tutor[];
	let isLoading = $state(false);

	async function handleSearch() {
		if (!searchQuery.trim()) return;

		isLoading = true;
		try {
			const response = await fetch(`/api/search/${encodeURIComponent(searchQuery)}`);
			const data = await response.json();
			searchResults = data as Tutor[];
		} catch (error) {
			console.error('Search failed:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen bg-neutral-100 p-6">
	<div class="mx-auto max-w-7xl">
		<section class="mb-8 rounded-2xl bg-white p-6 shadow-lg">
			<h2 class="mb-4 text-2xl font-bold text-gray-800">Search Tutors</h2>

			<div class="flex gap-4">
				<Field.Root class="flex-1 items-center justify-center">
					<Field.Label>Search</Field.Label>
					<input
						type="text"
						bind:value={searchQuery}
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								e.preventDefault();
								handleSearch();
							}
						}}
						placeholder="Search by course code or tutor name..."
						class="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-[#231161] focus:outline-none"
					/>
					<Field.ErrorText>No results found</Field.ErrorText>
				</Field.Root>

				<button
					onclick={handleSearch}
					disabled={isLoading}
					class="inline-flex items-center gap-2 rounded-lg bg-[#231161] px-4 py-2 text-white hover:bg-[#2d1982] disabled:bg-[#231161]/50"
				>
					<SearchIcon size={20} />
					{isLoading ? 'Searching...' : 'Search'}
				</button>
			</div>
		</section>

		{#if searchResults.length > 0}
			<section class="space-y-4">
				{#each searchResults as tutor}
					<div class="rounded-lg bg-white p-6 shadow-md">
						<div class="mb-4 flex items-center justify-between">
							<h3 class="text-xl font-semibold">{tutor.name}</h3>
							<span class="rounded-full bg-[#231161]/10 px-3 py-1 text-sm text-[#231161]">
								★ {tutor.rating}
							</span>
						</div>

						<div class="mb-2 text-gray-600">
							<p>Email: {tutor.email}</p>
							<p>Courses: {tutor.courses.join(', ')}</p>
						</div>

						{#if tutor.bio}
							<p class="mb-4 text-gray-700">{tutor.bio}</p>
						{/if}

						{#if tutor.posts.length > 0}
							<div class="border-t pt-4">
								<h4 class="mb-2 font-semibold">Recent Posts</h4>
								<div class="space-y-2">
									{#each tutor.posts as post}
										<div class="rounded-lg bg-gray-50 p-3">
											<p class="text-sm font-medium text-[#231161]">{post.course}</p>
											<p class="text-gray-700">{post.content}</p>
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</section>
		{:else if isLoading}
			<div class="text-center text-gray-600">Searching...</div>
		{:else if searchQuery}
			<div class="text-center text-gray-600">No results found</div>
		{/if}

		<section class="mt-8 rounded-2xl bg-white p-6 shadow-lg">
			<h2 class="mb-4 text-2xl font-bold text-gray-800">Filter Results</h2>

			<DatePicker.Root bind:value class="inline-flex flex-col gap-8">
				<!-- <DatePicker.Label>Select Date</DatePicker.Label> -->
				<DatePicker.Control class="inline-flex gap-4">
					<DatePicker.Input class="rounded-xl bg-neutral-50 p-2" />
					<DatePicker.Trigger
						class="rounded-xl bg-neutral-50 p-2 text-center hover:cursor-pointer hover:bg-neutral-200"
					>
						<CalendarIcon />
					</DatePicker.Trigger>
					<DatePicker.ClearTrigger class="p-2">Clear</DatePicker.ClearTrigger>
				</DatePicker.Control>
				<Portal>
					<DatePicker.Positioner>
						<DatePicker.Content class="rounded-2xl bg-neutral-50 p-4 drop-shadow-2xl">
							<!-- <DatePicker.YearSelect /> -->
							<!-- <DatePicker.MonthSelect /> -->
							<DatePicker.View view="day">
								<DatePicker.Context>
									{#snippet render(datePicker)}
										<DatePicker.ViewControl class="flex items-center justify-between">
											<DatePicker.PrevTrigger>
												<ChevronLeft
													class="rounded-full hover:cursor-pointer hover:bg-neutral-200"
												/>
											</DatePicker.PrevTrigger>
											<DatePicker.ViewTrigger>
												<DatePicker.RangeText />
											</DatePicker.ViewTrigger>
											<DatePicker.NextTrigger>
												<ChevronRight
													class="rounded-full hover:cursor-pointer hover:bg-neutral-200"
												/>
											</DatePicker.NextTrigger>
										</DatePicker.ViewControl>
										<DatePicker.Table>
											<DatePicker.TableHead>
												<DatePicker.TableRow>
													{#each datePicker().weekDays as weekDay}
														<DatePicker.TableHeader class="px-1"
															>{weekDay.short}</DatePicker.TableHeader
														>
													{/each}
												</DatePicker.TableRow>
											</DatePicker.TableHead>
											<DatePicker.TableBody>
												{#each datePicker().weeks as week}
													<DatePicker.TableRow>
														{#each week as day}
															<DatePicker.TableCell value={day} class="text-center">
																<DatePicker.TableCellTrigger
																	class="rounded-xl p-2 hover:cursor-pointer hover:bg-neutral-200 [&[data-disabled]]:cursor-default [&[data-disabled]]:text-neutral-400 [&[data-disabled]]:hover:bg-neutral-50 [&[data-today]]:text-red-500"
																	>{day.day}</DatePicker.TableCellTrigger
																>
															</DatePicker.TableCell>
														{/each}
													</DatePicker.TableRow>
												{/each}
											</DatePicker.TableBody>
										</DatePicker.Table>
									{/snippet}
								</DatePicker.Context>
							</DatePicker.View>
						</DatePicker.Content>
					</DatePicker.Positioner>
				</Portal>
			</DatePicker.Root>
		</section>
	</div>
</div>
