# juxt-desktop
Allows you to access Juxtaposition from a web browser\
(requires a Wii U)

# Setting up
1. Install [docker](https://www.docker.com/) and [git](https://git-scm.com/)
2. Clone the required repos:
```bash
git clone --recursive https://github.com/Milk-Cool/juxt-desktop.git
git clone https://github.com/PretendoNetwork/Inkay.git
```
3. Run the following:
```bash
docker run -it --rm -p 8082:8082 -v ./dumps:/home/mitmproxy/dumps ghcr.io/pretendonetwork/mitmproxy-nintendo:wiiu mitmdump
```
DO NOT CLOSE IT UNTIL TOLD TO DO SO!
4. In another window or tab, run the following:
```bash
docker ps
```
Make note of the container ID
5. Run:
```bash
docker cp CONTAINER_ID:/home/mitmproxy/.mitmproxy/mitmproxy-ca-cert.pem .
```
(replace `CONTAINER_ID` with your container ID)
6. Go to `Inkay/data`, and replace `ca.pem` with your `mitmproxy-ca-cert.pem`.
7. Compile Inkay by running following commands in the parent directory of `Inkay`:
```bash
docker build Inkay -t inkay-build
docker run -it --rm -v $(pwd)/Inkay:/app -w /app inkay-build
```
On Windows, run:
```bat
docker build Inkay -t inkay-build
docker run -it --rm -v %cd%/Inkay:/app -w /app inkay-build
```
8. `Inkay-pretendo.wps` should now appear in the `Inkay` directory. Copy it to `/fs/vol/external01/wiiu/environments/aroma/plugins` ON YOUR WII U, replacing the file if needed.
9. Reboot your Wii U.
10. Go to Wii U connection settings, select your active WiFi connection and in its settings, select "Proxy", set it to your computer's local address (which can be get via `ipconfig`), set port to 8082 and do not use any authentication. Perform a connection test and observe that there are some lines in the `mitmproxy` logs.
11. Open Miiverse, wait for it to load and precc Ctrl+C in `mitmproxy` ONCE. That will stop it and save the `.har` dump.
12. Open [the HAR analyzer](https://toolbox.googleapps.com/apps/har_analyzer/), and open your HAR dump which should be located at `dumps/wiiu-latest.har`.
13. Search for `service_token/@me`, then click on the only request on the left. On the right, copy the headers values to these environment variables (`set NAME=VALUE` on Windows, `export NAME=VALUE` on Unix-like):
```
X-Nintendo-System-Version -> SYSTEM_VERSION (no leading 0)
X-Nintendo-Serial-Number  -> SERIAL_NUMBER
X-Nintendo-Device-ID      -> DEVICE_ID
X-Nintendo-Region         -> REGION_ID
X-Nintendo-Country        -> COUNTRY_NAME
Accept-Language           -> LANGUAGE
```
14. Search for `generate`, then click on the request on the left and copy the header value of `X-Nintendo-Device-Cert` to environment variable `CERT`
15. On the right, switch to the tab `Post Data` and copy the value `user_id` to `USERNAME` and `password` to `PASSWORD`.
16. You can save the environment values somewhere, just please **DO NOT SHARE THEM**.
# Running
17. With the varialbes set, run the proxy using `mitmproxy -s juxt.py`.
18. Open a browser. Using an extension like FoxyProxy, set up a proxy pointing to `localhost` and port `8080`.
19. In the browser, open http://mitm.it. Download the certificate and install it in your browser's settings (google it).
20. Finally, open https://portal.olv.pretendo.cc. You're done! Juxt should show up at this point.