<script lang="ts">
    import { goto } from '$app/navigation';
</script>

<div class="flex min-h-screen items-center justify-center bg-neutral-100 px-4 py-12">
    <div class="w-full max-w-5xl">
        <!--header -->
        <div class="mb-12 text-center">
            <h1 class="mb-3 text-5xl font-bold text-[#231161]">Join Gator Guides</h1>
            <p class="text-xl text-gray-600">Choose how you'd like to register</p>
        </div>

        <!--registration option -->
        <div class="grid gap-8 md:grid-cols-2">
            <!--student registration card -->
            <div
                    class="group cursor-pointer rounded-2xl bg-white p-8 shadow-lg transition-all hover:scale-105 hover:shadow-2xl"
                    onclick={() => goto('/student-register')}                    role="button"
                    tabindex="0"
            >
                <div class="mb-6 flex justify-center">
                    <div
                            class="flex h-24 w-24 items-center justify-center rounded-full bg-[#231161] bg-opacity-10"
                    >
                        <svg
                                class="h-12 w-12 text-[#231161]"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                        >
                            <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                            />
                        </svg>
                    </div>
                </div>

                <h2 class="mb-4 text-center text-3xl font-bold text-[#231161]">Register as Student</h2>
                <p class="mb-6 text-center text-gray-600">
                    Looking for help with your courses? Register as a student to find and connect with
                    qualified tutors.
                </p>

                <ul class="mb-8 space-y-3">
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Search and browse available tutors</span>
                    </li>
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Book tutoring sessions</span>
                    </li>
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Get help from fellow SFSU students</span>
                    </li>
                </ul>

                <button
                        class="w-full rounded-lg bg-[#231161] px-6 py-4 text-lg font-semibold text-white transition-colors hover:bg-[#1a0d4a]"
                >
                    Register as Student →
                </button>
            </div>

            <!--tutor registration card -->
            <div
                    class="group cursor-pointer rounded-2xl bg-white p-8 shadow-lg transition-all hover:scale-105 hover:shadow-2xl"
                    onclick={() => goto('/tutor-register')}
                    role="button"
                    tabindex="0"
            >
                <div class="mb-6 flex justify-center">
                    <div
                            class="flex h-24 w-24 items-center justify-center rounded-full bg-[#231161] bg-opacity-10"
                    >
                        <svg
                                class="h-12 w-12 text-[#231161]"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                        >
                            <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                            />
                        </svg>
                    </div>
                </div>

                <h2 class="mb-4 text-center text-3xl font-bold text-[#231161]">Register as Tutor</h2>
                <p class="mb-6 text-center text-gray-600">
                    Share your knowledge and help fellow students succeed. Register as a tutor to start making
                    an impact.
                </p>

                <ul class="mb-8 space-y-3">
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Help students in subjects you excel at</span>
                    </li>
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Build your teaching experience</span>
                    </li>
                    <li class="flex items-start">
                        <svg class="mr-3 mt-1 h-5 w-5 flex-shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                            />
                        </svg>
                        <span class="text-gray-700">Make a difference in the SFSU community</span>
                    </li>
                </ul>

                <button
                        class="w-full rounded-lg bg-[#231161] px-6 py-4 text-lg font-semibold text-white transition-colors hover:bg-[#1a0d4a]"
                >
                    Register as Tutor →
                </button>
            </div>
        </div>

        <!--login link -->
        <div class="mt-12 text-center">
            <p class="text-gray-600">
                Already have an account?
                <a href="/login" class="font-medium text-[#231161] hover:underline">Sign in</a>
            </p>
        </div>

        <!--back to home -->
        <div class="mt-4 text-center">
            <a href="/" class="text-sm text-gray-600 hover:text-gray-800">← Back to home</a>
        </div>
    </div>
</div>