import subprocess
from pathlib import Path

from crontab import CronTab

from simplelinkedin.linkedin import LinkedIn
from simplelinkedin.ln_settings import LinkedInSettings


class LinkedInCron(LinkedIn):
    CRON_JOB_COMMENT = "LinkedInJob"

    @classmethod
    def set_smart_cron(cls, ln_settings: LinkedInSettings | dict):
        if isinstance(ln_settings, dict):
            ln_settings = LinkedInSettings(**ln_settings)

        python_path = [
            path.strip()
            for path in subprocess.run("which python", shell=True, capture_output=True).stdout.decode().split("\n")
        ][0]

        main_file_path = Path(__file__).absolute().parent

        if ln_settings.LINKEDIN_CRON_ENV:
            env_file = Path(ln_settings.LINKEDIN_CRON_ENV).absolute()

            command = f"{python_path or 'python'} {main_file_path} --env {env_file}"
        else:
            print("You must provide cronfile to set crons.")
            exit(1)

        cron = CronTab(user=ln_settings.LINKEDIN_CRON_USER)

        even_day_job = cron.new(command=command, comment=cls.CRON_JOB_COMMENT)
        even_day_job.hour.on(20)
        even_day_job.dow.on(0, 2, 4, 6)

        odd_day_job = cron.new(command=command, comment=cls.CRON_JOB_COMMENT)
        odd_day_job.hour.on(22)
        odd_day_job.dow.on(1, 3, 5)

        cron.write()

    @classmethod
    def remove_cron_jobs(cls, ln_settings: dict | LinkedInSettings):
        """Remove cron jobs set by the module earlier with the comment specified by CRON_JOB_COMMENT var"""

        if isinstance(ln_settings, dict):
            ln_settings = LinkedInSettings(**ln_settings)

        cron = CronTab(user=ln_settings.LINKEDIN_CRON_USER)
        cron.remove_all(comment=cls.CRON_JOB_COMMENT)
        cron.write()


if __name__ == "__main__":
    settings = {
        "LINKEDIN_USER": "<username>",
        "LINKEDIN_PASSWORD": "<password>",
        "LINKEDIN_BROWSER": "Chrome",
        "LINKEDIN_BROWSER_HEADLESS": 0,
        "LINKEDIN_BROWSER_CRON": 0,
        "LINKEDIN_CRON_USER": "<root_user>",
        "LINKEDIN_PREFERRED_USER": "/path/to/preferred/user/text_doc.text",
        "LINKEDIN_NOT_PREFERRED_USER": "/path/to/not/preferred/user/text_doc.text",
    }

    with LinkedInCron(
        username=settings.get("LINKEDIN_USER"),
        password=settings.get("LINKEDIN_PASSWORD"),
        browser=settings.get("LINKEDIN_BROWSER"),
        headless=bool(settings.get("LINKEDIN_BROWSER_HEADLESS")),
    ) as ln:
        # remove existing cron jobs
        ln.remove_cron_jobs(ln_settings=settings)

        # set cron on your machine
        ln.set_smart_cron(settings)
