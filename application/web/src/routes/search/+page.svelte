<script lang="ts">
    import { DatePicker, parseDate } from '@ark-ui/svelte/date-picker';
    import { Field } from '@ark-ui/svelte/field';
    import { Portal } from '@ark-ui/svelte/portal';
    import { CalendarIcon, ChevronLeft, ChevronRight, Search as SearchIcon } from '@lucide/svelte';
    import { browser } from '$app/environment';
    import { searchTutors, type SearchResult } from '$lib/api';

    const today = new Date();
    const formatted = today.toISOString().split('T')[0];
    let value = $state([parseDate(formatted)]);

    interface Tutor {
        name: string;
        rating?: number;
        email?: string;
        courses: string[];
        bio?: string | null;
        posts: { course: string; content: string }[];
    }

    // Search state
    let searchQuery = $state('');
    let searchResults = $state([]) as Tutor[];
    let isLoading = $state(false);
    let errorMessage = $state('');

    async function handleSearch() {
        const q = searchQuery.trim();
        if (!q) {
            searchResults = [];
            errorMessage = '';
            return;
        }

        isLoading = true;
        errorMessage = '';
        searchResults = [];

        try {
            // Use shared API helper so it's consistent with the rest of the app
            const data: SearchResult[] = await searchTutors(q);

            // Map backend SearchResult -> local Tutor shape
            searchResults = data.map((t) => ({
                name: t.name,
                rating: t.rating,
                email: t.email,
                courses: t.courses ?? [],
                bio: t.bio,
                posts: (t.posts ?? []).map((p) => ({
                    course: p.course,
                    content: p.content
                }))
            }));

            if (searchResults.length === 0) {
                errorMessage = 'No tutors found for that search.';
            }
        } catch (error: any) {
            console.error('Search failed:', error);
            errorMessage = error?.message ?? 'Search failed. Please try again.';
        } finally {
            isLoading = false;
        }
    }

    // Auto-run search if ?search=... is in the URL
    if (browser) {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('search')) {
            searchQuery = urlParams.get('search') ?? '';
            if (searchQuery.trim()) {
                handleSearch();
            }
        }
    }
</script>

<div class="min-h-screen bg-neutral-100 p-6">
    <div class="mx-auto max-w-7xl">
        <section class="mb-8 rounded-2xl bg-white p-6 shadow-lg">
            <h2 class="mb-4 text-2xl font-bold text-gray-800">Search Tutors</h2>

            <Field.Root class="flex flex-col items-center justify-center gap-4 sm:flex-row">
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
                        class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 focus:border-[#231161] focus:outline-none"
                />
                {#if errorMessage}
                    <Field.ErrorText>{errorMessage}</Field.ErrorText>
                {/if}
                <button
                        onclick={handleSearch}
                        disabled={isLoading}
                        class="inline-flex w-full items-center gap-2 rounded-lg bg-[#231161] px-4 py-2 text-white hover:bg-[#2d1982] disabled:bg-[#231161]/50 sm:w-auto"
                >
                    <SearchIcon size={20} />
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </Field.Root>
        </section>

        {#if searchResults.length > 0}
            <section class="space-y-4">
                {#each searchResults as tutor}
                    <div class="rounded-lg bg-white p-6 shadow-md">
                        <div class="mb-4 flex items-center justify-between">
                            <h3 class="text-xl font-semibold">{tutor.name}</h3>
                            {#if tutor.rating !== undefined}
								<span class="rounded-full bg-[#231161]/10 px-3 py-1 text-sm text-[#231161]">
									★ {tutor.rating}
								</span>
                            {/if}
                        </div>

                        <div class="mb-2 text-gray-600">
                            {#if tutor.email}
                                <p>Email: {tutor.email}</p>
                            {/if}
                            {#if tutor.courses && tutor.courses.length > 0}
                                <p>Courses: {tutor.courses.join(', ')}</p>
                            {/if}
                        </div>

                        {#if tutor.bio}
                            <p class="mb-4 text-gray-700">{tutor.bio}</p>
                        {/if}

                        {#if tutor.posts && tutor.posts.length > 0}
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
        {:else if searchQuery && !isLoading && !errorMessage}
            <div class="text-center text-gray-600">No results found</div>
        {/if}

        <section class="mt-8 rounded-2xl bg-white p-6 shadow-lg">
            <h2 class="mb-4 text-2xl font-bold text-gray-800">Filter Results</h2>

            <DatePicker.Root bind:value class="inline-flex flex-col gap-8">
                <DatePicker.Control class="inline-flex gap-4">
                    <DatePicker.Input
                            class="rounded-lg border border-gray-300 bg-white px-4 py-2 focus:border-[#231161] focus:outline-none"
                    />
                    <DatePicker.Trigger
                            class="rounded-lg border border-gray-300 bg-white p-2 hover:cursor-pointer focus:border-[#231161] focus:outline-none"
                    >
                        <CalendarIcon />
                    </DatePicker.Trigger>
                    <DatePicker.ClearTrigger class="p-2">Clear</DatePicker.ClearTrigger>
                </DatePicker.Control>
                <Portal>
                    <DatePicker.Positioner>
                        <DatePicker.Content class="rounded-2xl bg-neutral-50 p-4 shadow-lg">
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
