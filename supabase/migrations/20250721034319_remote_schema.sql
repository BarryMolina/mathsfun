create table "public"."problem_attempts" (
    "id" uuid not null default gen_random_uuid(),
    "session_id" uuid not null,
    "problem" text not null,
    "user_answer" integer,
    "correct_answer" integer not null,
    "is_correct" boolean not null,
    "response_time_ms" integer not null,
    "timestamp" timestamp with time zone default now()
);


alter table "public"."problem_attempts" enable row level security;

create table "public"."quiz_sessions" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" uuid not null,
    "quiz_type" text not null,
    "difficulty_level" integer not null,
    "start_time" timestamp with time zone default now(),
    "end_time" timestamp with time zone,
    "total_problems" integer default 0,
    "correct_answers" integer default 0,
    "status" text default 'active'::text
);


alter table "public"."quiz_sessions" enable row level security;

create table "public"."user_profiles" (
    "id" uuid not null,
    "display_name" text,
    "created_at" timestamp with time zone default now(),
    "last_active" timestamp with time zone default now()
);


alter table "public"."user_profiles" enable row level security;

CREATE INDEX idx_problem_attempts_session_id ON public.problem_attempts USING btree (session_id);

CREATE INDEX idx_problem_attempts_timestamp ON public.problem_attempts USING btree ("timestamp");

CREATE INDEX idx_quiz_sessions_created ON public.quiz_sessions USING btree (start_time);

CREATE INDEX idx_quiz_sessions_status ON public.quiz_sessions USING btree (status);

CREATE INDEX idx_quiz_sessions_user_id ON public.quiz_sessions USING btree (user_id);

CREATE INDEX idx_user_profiles_last_active ON public.user_profiles USING btree (last_active);

CREATE UNIQUE INDEX problem_attempts_pkey ON public.problem_attempts USING btree (id);

CREATE UNIQUE INDEX quiz_sessions_pkey ON public.quiz_sessions USING btree (id);

CREATE UNIQUE INDEX user_profiles_pkey ON public.user_profiles USING btree (id);

alter table "public"."problem_attempts" add constraint "problem_attempts_pkey" PRIMARY KEY using index "problem_attempts_pkey";

alter table "public"."quiz_sessions" add constraint "quiz_sessions_pkey" PRIMARY KEY using index "quiz_sessions_pkey";

alter table "public"."user_profiles" add constraint "user_profiles_pkey" PRIMARY KEY using index "user_profiles_pkey";

alter table "public"."problem_attempts" add constraint "problem_attempts_session_id_fkey" FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE not valid;

alter table "public"."problem_attempts" validate constraint "problem_attempts_session_id_fkey";

alter table "public"."problem_attempts" add constraint "valid_response_time" CHECK ((response_time_ms > 0)) not valid;

alter table "public"."problem_attempts" validate constraint "valid_response_time";

alter table "public"."quiz_sessions" add constraint "quiz_sessions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE not valid;

alter table "public"."quiz_sessions" validate constraint "quiz_sessions_user_id_fkey";

alter table "public"."quiz_sessions" add constraint "valid_correct" CHECK (((correct_answers >= 0) AND (correct_answers <= total_problems))) not valid;

alter table "public"."quiz_sessions" validate constraint "valid_correct";

alter table "public"."quiz_sessions" add constraint "valid_difficulty" CHECK (((difficulty_level >= 1) AND (difficulty_level <= 5))) not valid;

alter table "public"."quiz_sessions" validate constraint "valid_difficulty";

alter table "public"."quiz_sessions" add constraint "valid_problems" CHECK ((total_problems >= 0)) not valid;

alter table "public"."quiz_sessions" validate constraint "valid_problems";

alter table "public"."quiz_sessions" add constraint "valid_quiz_type" CHECK ((quiz_type = ANY (ARRAY['addition'::text, 'tables'::text]))) not valid;

alter table "public"."quiz_sessions" validate constraint "valid_quiz_type";

alter table "public"."quiz_sessions" add constraint "valid_status" CHECK ((status = ANY (ARRAY['active'::text, 'completed'::text, 'abandoned'::text]))) not valid;

alter table "public"."quiz_sessions" validate constraint "valid_status";

alter table "public"."user_profiles" add constraint "user_profiles_id_fkey" FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE not valid;

alter table "public"."user_profiles" validate constraint "user_profiles_id_fkey";

alter table "public"."user_profiles" add constraint "valid_display_name" CHECK ((char_length(display_name) >= 1)) not valid;

alter table "public"."user_profiles" validate constraint "valid_display_name";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.update_last_active()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
BEGIN
    UPDATE public.user_profiles 
    SET last_active = NOW() 
    WHERE id = auth.uid();
    RETURN NULL;
END;
$function$
;

grant delete on table "public"."problem_attempts" to "anon";

grant insert on table "public"."problem_attempts" to "anon";

grant references on table "public"."problem_attempts" to "anon";

grant select on table "public"."problem_attempts" to "anon";

grant trigger on table "public"."problem_attempts" to "anon";

grant truncate on table "public"."problem_attempts" to "anon";

grant update on table "public"."problem_attempts" to "anon";

grant delete on table "public"."problem_attempts" to "authenticated";

grant insert on table "public"."problem_attempts" to "authenticated";

grant references on table "public"."problem_attempts" to "authenticated";

grant select on table "public"."problem_attempts" to "authenticated";

grant trigger on table "public"."problem_attempts" to "authenticated";

grant truncate on table "public"."problem_attempts" to "authenticated";

grant update on table "public"."problem_attempts" to "authenticated";

grant delete on table "public"."problem_attempts" to "service_role";

grant insert on table "public"."problem_attempts" to "service_role";

grant references on table "public"."problem_attempts" to "service_role";

grant select on table "public"."problem_attempts" to "service_role";

grant trigger on table "public"."problem_attempts" to "service_role";

grant truncate on table "public"."problem_attempts" to "service_role";

grant update on table "public"."problem_attempts" to "service_role";

grant delete on table "public"."quiz_sessions" to "anon";

grant insert on table "public"."quiz_sessions" to "anon";

grant references on table "public"."quiz_sessions" to "anon";

grant select on table "public"."quiz_sessions" to "anon";

grant trigger on table "public"."quiz_sessions" to "anon";

grant truncate on table "public"."quiz_sessions" to "anon";

grant update on table "public"."quiz_sessions" to "anon";

grant delete on table "public"."quiz_sessions" to "authenticated";

grant insert on table "public"."quiz_sessions" to "authenticated";

grant references on table "public"."quiz_sessions" to "authenticated";

grant select on table "public"."quiz_sessions" to "authenticated";

grant trigger on table "public"."quiz_sessions" to "authenticated";

grant truncate on table "public"."quiz_sessions" to "authenticated";

grant update on table "public"."quiz_sessions" to "authenticated";

grant delete on table "public"."quiz_sessions" to "service_role";

grant insert on table "public"."quiz_sessions" to "service_role";

grant references on table "public"."quiz_sessions" to "service_role";

grant select on table "public"."quiz_sessions" to "service_role";

grant trigger on table "public"."quiz_sessions" to "service_role";

grant truncate on table "public"."quiz_sessions" to "service_role";

grant update on table "public"."quiz_sessions" to "service_role";

grant delete on table "public"."user_profiles" to "anon";

grant insert on table "public"."user_profiles" to "anon";

grant references on table "public"."user_profiles" to "anon";

grant select on table "public"."user_profiles" to "anon";

grant trigger on table "public"."user_profiles" to "anon";

grant truncate on table "public"."user_profiles" to "anon";

grant update on table "public"."user_profiles" to "anon";

grant delete on table "public"."user_profiles" to "authenticated";

grant insert on table "public"."user_profiles" to "authenticated";

grant references on table "public"."user_profiles" to "authenticated";

grant select on table "public"."user_profiles" to "authenticated";

grant trigger on table "public"."user_profiles" to "authenticated";

grant truncate on table "public"."user_profiles" to "authenticated";

grant update on table "public"."user_profiles" to "authenticated";

grant delete on table "public"."user_profiles" to "service_role";

grant insert on table "public"."user_profiles" to "service_role";

grant references on table "public"."user_profiles" to "service_role";

grant select on table "public"."user_profiles" to "service_role";

grant trigger on table "public"."user_profiles" to "service_role";

grant truncate on table "public"."user_profiles" to "service_role";

grant update on table "public"."user_profiles" to "service_role";

create policy "Users can insert own attempts"
on "public"."problem_attempts"
as permissive
for insert
to public
with check ((auth.uid() = ( SELECT quiz_sessions.user_id
   FROM quiz_sessions
  WHERE (quiz_sessions.id = problem_attempts.session_id))));


create policy "Users can view own attempts"
on "public"."problem_attempts"
as permissive
for select
to public
using ((auth.uid() = ( SELECT quiz_sessions.user_id
   FROM quiz_sessions
  WHERE (quiz_sessions.id = problem_attempts.session_id))));


create policy "Users can insert own sessions"
on "public"."quiz_sessions"
as permissive
for insert
to public
with check ((auth.uid() = user_id));


create policy "Users can update own sessions"
on "public"."quiz_sessions"
as permissive
for update
to public
using ((auth.uid() = user_id));


create policy "Users can view own sessions"
on "public"."quiz_sessions"
as permissive
for select
to public
using ((auth.uid() = user_id));


create policy "Users can insert own profile"
on "public"."user_profiles"
as permissive
for insert
to public
with check ((auth.uid() = id));


create policy "Users can update own profile"
on "public"."user_profiles"
as permissive
for update
to public
using ((auth.uid() = id));


create policy "Users can view own profile"
on "public"."user_profiles"
as permissive
for select
to public
using ((auth.uid() = id));


CREATE TRIGGER trigger_update_last_active AFTER INSERT ON public.quiz_sessions FOR EACH ROW EXECUTE FUNCTION update_last_active();


