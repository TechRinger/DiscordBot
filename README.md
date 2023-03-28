


<br />
<div align="center">

  <h3 align="center"><b>Discord Bot</b></h3>

  <p align="center">
    An awesome Discord bot using XSOAR and ChatGPT!
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#Enviromental Variables">Enviromental Variables</a></li>  
    <li><a href="#Sample Deplyoment">Sample Deplyoment</a></li>
    <li><a href="#Roadmap">Roadmap</a></li>
    <li><a href="#installation">Installation</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project



This project is designed to showcase how chat programs (Discord in this case) can be used as a easy to use front end for automation systems.

Here's why Discord:
* It's free to use so everyone can set it up thier own Bot!
* Discord can be used to intigrate into many automation workflows including GitHub Actions
* I'm a gamer so I live on Discord anyway :wink:


<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Enviromental Variables

This section lists out the enviromental varaibles used in the container
| ENV | Desc | Sample Value | Helpful info/URL|
|---|---|---|---|
| DISCORD_BOT_TOKEN | Token used to talk to Discord as the Bot | N00b$AfdQ.fddkpP7.P345fgdsJfiwKZJH1Jxfdf3 |https://discord.com/developers/docs/topics/oauth2#bots|
| DISCORD_GUILD | Name of the Discord Guild |N00bs Only  |https://discord.com/developers/docs/resources/guild|
| XSOAR_URL |The URL for the XSOAR instance  |https://xsoar.example.com  |https://www.paloaltonetworks.com/cortex/cortex-xsoar|
| XSOAR_PLAYBOOK |XSOAR playbook ID  | 9969b7b3-ed19-4d7f-8de2-a165b153f557 | When listing playbooks the ID can be seen by looking at the response|
| OPENAI_API_TOKEN | Token used to talk to OpenAI (CHatGPT) | im-an00b-tdfjm3kj132fNGvE8jG3T3BlbkFJXnSm9Idsfaj3k32j4 |https://platform.openai.com/signup|
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Sample Deplyoment

This is an example of how you could use a helm release to deploy the bot into your kubernetes enviroment.


* Kubernetes Deployment using external secrets for ENV
  ```yaml
    apiVersion: helm.toolkit.fluxcd.io/v2beta1
    kind: HelmRelease
    metadata:
    name: discord-xsoar
    namespace: bots
    spec:
    interval: 15m
    chart:
        spec:
        chart: app-template
        version: 1.3.2
        sourceRef:
            kind: HelmRepository
            name: bjw-s
            namespace: flux-system
    maxHistory: 3
    install:
        createNamespace: true
        remediation:
        retries: 3
    upgrade:
        cleanupOnFail: true
        remediation:
        retries: 3
    uninstall:
        keepHistory: false
    values:
        service:
        main:
            ports:
            http:
                port: &port 8080
        probes:
            liveness: &probes
                enabled: true
                custom: true
                spec:
                exec:
                    command:
                    - cat
                    - /bot/bot/bot.py
                initialDelaySeconds: 5
                periodSeconds: 5
            readiness: *probes
            startup:
                enabled: false
        image:
        repository: ghcr.io/techringer/discordbot
        tag: latest
        pullPolicy: Always

        # env:
        #   ...
        envFrom:
        - secretRef:
            name: discord-xsoar-secret
  ```
  * External Secrets pulling from onepassword key called `bots`
  ```yaml
  apiVersion: external-secrets.io/v1beta1
    kind: ExternalSecret
    metadata:
    name: discord-xsoar
    namespace: bots
    spec:
    secretStoreRef:
        kind: ClusterSecretStore
        name: onepassword-connect
    target:
        name: discord-xsoar-secret
        creationPolicy: Owner
    data:
        - secretKey: DISCORD_BOT_TOKEN
        remoteRef:
            key: bots
            property: DISCORD_BOT_TOKEN
        - secretKey: XSOAR_API
        remoteRef:
            key: bots
            property: XSOAR_API
        - secretKey: DISCORD_GUILD
        remoteRef:
            key: bots
            property: DISCORD_GUILD
        - secretKey: OPENAI_API_TOKEN
        remoteRef:
            key: bots
            property: OPENAI_API_TOKEN
        - secretKey: XSOAR_BOT_TOKEN
        remoteRef:
            key: bots
            property: XSOAR_BOT_TOKEN
        - secretKey: XSOAR_URL
        remoteRef:
            key: bots
            property: XSOAR_URL
        - secretKey: XSOAR_PLAYBOOK
        remoteRef:
            key: bots
            property: XSOAR_PLAYBOOK
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Vul-Lab creation
  - [ ] Validate Vul-Lab instance before creating another for the user/email
- [ ] Add IOC submittal/check
- [ ] Add CVE enviroment creation
- [ ] Add GOAT enviroment creation

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

