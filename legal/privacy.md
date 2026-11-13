# Privacy Policy

**Version 1.0 · Last updated: November 13, 2026**

## 1. Who this policy covers

Bargaz is a personal project operated by Devon Finney-Gaitan ("we," "us"). It is operated from Eugene, Oregon, and during the school year from Corvallis, Oregon. Legally, the operator is located in Eugene, Oregon.

This policy covers every site and service under Bargaz, including:

- bargaz.app
- bot.bargaz.app (BargazBot information)
- live.bargaz.app (BargazLive)
- randomwolf08.com (RandomWolf08, including content-creator profiles)
- BargazBot, the Discord bot
- The public status endpoints at bargaz.app/status
- Bargaz software and related projects

Some of these may become separate products with their own policies later. Until then, this policy applies to all of them.

## 2. The short version

- There are no user accounts or passwords on the sites.
- We do not sell personal information.
- The sites set almost no cookies of their own. Settings are stored in your browser and tied to a random ID.
- Google AdSense shows ads on most pages, and Google uses its own cookies to serve them.
- Server logs are kept until they are removed manually. Copies may remain in private Discord debugging channels.
- Public status pages show the health and network state of the server.
- BargazBot stores Discord server and member identifiers, and the settings you choose for it.

## 3. Information we collect

**3.1 Appearance settings.** When you change theme, contrast, or colorblind options, your browser creates a random ID. Your settings are stored on our server under that ID so they follow you between our sites. The ID contains no name, email, or account information.

**3.2 Information in URLs.** When you move between Bargaz sites, your appearance ID is added to the address as a query parameter (`bargazAppearanceLink`). Browsers record that address in your history, and it can appear in any server request log.

**3.3 Server logs.** The Bargaz server writes system logs, including startup messages, errors, and events from BargazBot. These can include error details and identifiers the software needs to function. The sites' web server does not write a per-visit access log. Requests are logged by Cloudflare, described in section 6.

**3.4 Public status information.** The status pages at bargaz.app/status publish the health of the server that runs Bargaz:

- Power source, battery level, and shutdown state
- The server's network connection: connection type (Wi-Fi or Ethernet), whether it is connected, signal strength, and interface names
- Storage, component checks, installed versions, and backup status
- Timestamps

This describes the server, not visitors. Anyone can read it.

**3.5 Analytics.** Cloudflare Web Analytics on bargaz.app and randomwolf08.com records page views, referrers, country, and device type in aggregate. It does not use cookies or track individuals across sites.

**3.6 Messages you send us.** If you email us or contact us on Discord, we receive what you include.

**3.7 BargazBot data.** When BargazBot is added to a Discord server, it stores:

- Discord server IDs and names
- Server owner's Discord ID
- Channel IDs for the features you configure (announcements, welcome, goodbye, logs, updates, status)
- Member IDs for the server's members (kept current for permissions and cleanup)
- Role and user IDs used for permission settings
- Custom notification text that server administrators write for YouTube, Twitch, or Kick posts
- IDs of notifications the bot has posted, to prevent duplicates
- Entitlement records for paid or free features, linked to a Discord user ID
- Deletion requests, with their expiry dates

BargazBot does not store message text, usernames, email addresses, or payment details. It does not store the content of welcome or goodbye messages, only the channel where they are posted.

**3.8 Things we do not collect.** Passwords, accounts, payment card details, precise location, contact lists, or advertising profiles of our own.

## 4. Cookies and local storage

We do not set cookies of our own. The sites use your browser's local storage for:

- `bargaz-appearance-id`: your random ID
- `bargaz-theme`, `bargaz-high-contrast`, `bargaz-colorblind`: your display settings
- `bargazAppearanceLink`: a short-lived value that carries your ID between sites in the address bar (section 3.2)

Clearing site data in your browser removes all of these.

Cloudflare may set security cookies, such as `__cf_bm`, to tell people apart from automated traffic.

Google's ad cookies are described in section 5.

## 5. Advertising

Ads are shown on pages across the sites, except the raw JSON status endpoints. Ads may not appear on every page or every visit.

Ads are provided by Google AdSense. Google and its partners may use cookies and similar identifiers to show ads, including personalized ads based on your visits to this and other sites. We do not control those identifiers and do not receive your name or contact details from Google. We receive aggregate reports and estimated earnings.

- **EEA, UK, and Switzerland:** we use Google's certified consent tool before loading advertising cookies. You can change or withdraw consent at any time through the privacy link Google shows with the ads.
- **Other regions:** Google may show a privacy notice and options as required by local law.
- **Limiting personalized ads:** use [Google Ads Settings](https://adssettings.google.com), [aboutads.info](https://www.aboutads.info), or [youronlinechoices.eu](https://www.youronlinechoices.eu). Opting out does not remove ads.

## 6. Cloudflare

All traffic to our sites passes through Cloudflare. Cloudflare provides DNS, domain registration, content delivery, security, and analytics. Cloudflare sees each request, including its IP address, page, time, and browser information, and keeps request logs under its own policies. Cloudflare also hides email addresses displayed on our pages from automated scrapers, but people can still see them.

## 7. How we use information

- Run, secure, and troubleshoot the sites and services
- Remember your display settings
- Operate BargazBot and its features, including notifications, permissions, and cleanup
- Publish the status information described in section 3.4
- Answer messages you send us
- Understand aggregate traffic
- Serve advertising through Google
- Meet legal obligations and protect rights and safety

We do not build advertising or marketing profiles of individuals. Google may build profiles through its own cookies, as described in section 5.

## 8. Who we share information with

We share information only with the services needed to run Bargaz:

- **Cloudflare:** DNS, security, delivery, analytics (section 6)
- **Google:** advertising and consent (section 5)
- **Discord:** the bot and Discord features; Discord's own policies apply
- **YouTube, Twitch, and Kick:** we send requests for public channel and content information. We do not send personal information to them.
- **GitHub:** we read public documentation and content from GitHub. We send no personal information.
- **UptimeRobot:** monitors the public status endpoint. It receives the status information only.
- **Email provider:** receives and holds messages you send us.
- **Authorities:** when the law requires it, or when necessary to protect rights or safety.

We do not sell personal information and do not share it with data brokers. Donations and any future paid features will be handled by a third-party payment provider, which will collect payment details under its own policy. We do not store payment card details.

## 9. Where information is processed

The Bargaz server is in Eugene, Oregon, or Corvallis, Oregon, depending on the time of year. Cloudflare, Google, Discord, and the other providers process information in the United States and elsewhere. Where the law requires safeguards for transfers outside your country, we rely on the safeguards those providers offer.

## 10. Who can access information

**Public:** the status pages and the public Discord status channel, which shows the server's network connection and status updates.

**Private:** the bot's console and errors channels in the owner's Discord server. Only users with administrator access to that server can see them. These channels contain system logs and debugging information.

**Server access:** only the operator can access the Pi.

**BargazBot in other servers:** each server's administrators decide who can view and manage BargazBot there, and at what level. Those administrators are responsible for how the people they grant access use the bot. Bargaz does not control those settings.

## 11. How long we keep information

- **Appearance settings:** until you clear your browser data or the record is removed. The store keeps at most 10,000 records and removes the oldest first.
- **Server logs:** kept until removed manually. Copies may be saved in private Discord debugging channels, where they are kept until removed there.
- **Status information:** only the latest status is published; history is kept as backups or logs.
- **Analytics:** aggregate data, kept under Cloudflare's policies.
- **BargazBot data:**
  - Data for a server is removed in a daily cleanup after the bot leaves that server.
  - Data is removed when a server or user requests deletion with the `/data delete` command.
  - Deletion request records are removed once they expire.
- **Backups:** the bot's database is backed up hourly, daily, and weekly. Backups are kept for about five weeks. Data deleted from the live database can remain in backups until they roll off.
- **Messages you send us:** as long as needed to handle them, plus a reasonable record afterward.
- **Advertising data:** controlled by Google.

We do not keep information longer than we need it.

## 12. Security

Traffic to the sites uses HTTPS. The server is protected by security measures, and access is limited to the operator. The bot runs a small web service on the server that is not intended for public use. We store as little information as possible. No system is perfectly secure, so we cannot promise absolute security.

## 13. Your choices and rights

- **Browser:** clear site data to remove your settings and ID.
- **Ads:** change consent in the Google privacy link, or limit personalized ads through the links in section 5.
- **BargazBot:** a server administrator can run `/data delete`, or remove BargazBot from the server. Users can ask us to delete their data (section 14).
- **Requests:** email us to find out what is stored under your ID or to ask for correction or deletion. We may need to confirm the ID belongs to you. We aim to respond within 30 days.
- **EEA and UK:** you may complain to your local data protection authority.

Deleted data may remain in backups for up to about five weeks, as described in section 11.

## 14. Deletion requests

To request deletion of BargazBot data for your Discord account or a server, email us from the address you want to delete under, or contact us on Discord. We will remove the data from the live database. Backups are cleared on their normal schedule.

## 15. Children

The websites have no minimum age requirement. Where a platform or service sets its own minimum age, that minimum applies. BargazBot follows Discord's minimum age. For any service without a platform minimum, we advise that you be at least 13. We do not knowingly collect information from children below these ages. If we learn that we have, we will delete it.

## 16. Do Not Track and Global Privacy Control

We do not track you across other websites. Advertising partners handle browser privacy signals under their own policies.

## 17. Links and third-party services

The sites link to external services, including Discord, GitHub, YouTube, Twitch, Kick, Linktree, and others. We may add more over time. External links open after a confirmation notice. Those services have their own privacy policies, and we are not responsible for them.

## 18. Changes to this policy

We may update this policy. The version and date at the top show the current version. Changes are versioned as follows:

- **Patch (1.0.1):** typo fixes and corrections that do not change meaning.
- **Minor (1.1):** small clarifications or additions that do not change how data is handled.
- **Major (2.0):** new clauses, new features, or changes to what we collect or share.

Significant changes will be noted on the sites.

## 19. Contact

Questions about this policy: **devon6608@gmail.com**, or the [Contact page](https://bargaz.app/contact).
