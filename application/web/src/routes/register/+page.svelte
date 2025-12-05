<script lang="ts">
    // this page is just a chooser between student and tutor registration
</script>

<div class="min-h-screen bg-neutral-100 p-6">
    <div class="mx-auto max-w-4xl">
        <section class="rounded-2xl bg-white p-8 shadow-xl border border-gray-100 mt-6">
            <h1 class="mb-2 text-3xl font-bold text-[#231161] text-center">Create your account</h1>
            <p class="mb-8 text-sm text-gray-600 text-center">
                Choose how you want to use Gator Guides.
            </p>

            <div class="grid gap-6 md:grid-cols-2">
                <!-- Student card -->
                <a
                        href="/student-register"
                        class="group flex flex-col justify-between rounded-2xl border border-gray-200 bg-neutral-50 p-6 hover:border-[#231161] hover:bg-white hover:shadow-md transition-colors"
                >
                    <div>
                        <h2 class="mb-2 text-xl font-semibold text-gray-900">Student registration</h2>
                        <p class="text-sm text-gray-600">
                            Book tutoring sessions, track your upcoming appointments, and connect with verified SFSU
                            tutors.
                        </p>
                    </div>
                    <div class="mt-4 text-sm font-semibold text-[#231161] group-hover:underline">
                        Continue as a student &rarr;
                    </div>
                </a>

                <!-- Tutor card -->
                <a
                        href="/tutor-register"
                        class="group flex flex-col justify-between rounded-2xl border border-gray-200 bg-neutral-50 p-6 hover:border-[#231161] hover:bg-white hover:shadow-md transition-colors"
                >
                    <div>
                        <h2 class="mb-2 text-xl font-semibold text-gray-900">Tutor registration</h2>
                        <p class="text-sm text-gray-600">
                            Apply to become a tutor, list the courses you can help with, and get matched with students
                            who need support.
                        </p>
                    </div>
                    <div class="mt-4 text-sm font-semibold text-[#231161] group-hover:underline">
                        Continue as a tutor &rarr;
                    </div>
                </a>
            </div>

            <p class="mt-6 text-center text-xs text-gray-600">
                Already have an account?
                <a href="/login" class="text-[#231161] hover:underline">Sign in</a>.
            </p>
        </section>
    </div>
</div>
