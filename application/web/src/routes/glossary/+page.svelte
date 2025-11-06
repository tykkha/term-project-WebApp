<script lang="ts">
	import { DatePicker, parseDate } from '@ark-ui/svelte/date-picker';
	import { Portal } from '@ark-ui/svelte/portal';
	import { CalendarIcon, ChevronLeft, ChevronRight } from '@lucide/svelte';
	const today = new Date();
	const year = today.getFullYear();
	const month = String(today.getMonth() + 1).padStart(2, '0');
	const day = String(today.getDate()).padStart(2, '0');
	const formatted = `${year}-${month}-${day}`;
	let value = $state([parseDate(formatted)]);
</script>

<div class="h-screen w-screen bg-neutral-300">
	<div class="rounded-2xl bg-neutral-200 p-4 drop-shadow-lg">
		<p class="text-xl font-bold">Filters</p>
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
											<ChevronLeft class="rounded-full hover:cursor-pointer hover:bg-neutral-200" />
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
																class="rounded-xl p-2 hover:cursor-pointer hover:bg-neutral-200 [&[data-disabled]]:text-neutral-400 [&[data-today]]:text-red-500"
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
	</div>
</div>
