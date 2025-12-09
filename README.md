# E-ink Dashboard

An open-source, mini, functional E-ink dashboard! As seen on [my YouTube channel](https://www.youtube.com/channel/UCPqrW35BnRePrjOEAL8YBVg).

## What This Does

This project turns your E-ink display into a smart information hub that can show:
- **Clock**: Current time and date with customizable fonts
- **Weather**: Local weather forecasts with beautiful icons  
- **Stocks**: Real-time stock prices for your favorite companies
- **YouTube**: Channel statistics and growth tracking

The best part? You can set it to automatically cycle through different dashboards at whatever interval you choose, or control it manually through a simple web interface. Change settings over wifi with your phone or computer and get live feedback from the display!

## What You'll Need

### Hardware
- **Raspberry Pi** (I use the [Raspberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/). If you're not comforatble with soldering, just buy one with the headers on it already)
- **E-ink Display** (I use [this 2.13" Waveshare Pi Hat Display](https://www.waveshare.com/2.13inch-e-Paper-HAT.htm)) display
- **MicroSD Card** (16GB or larger recommended, and make sure it's at least A1 rated or something, I'd just use whatever Raspberry Pi recommends)
- **Power Supply** (for your Pi, or like a microUSB cable to your PC)

### Skills Required
- **Beginner Friendly!** This guide assumes you're new to Raspberry Pi
- Basic comfort with copying/pasting commands
- Patience for the initial setup (about 30-45 minutes)
- Understanding that I'm just some guy and this code may be prone to breaking and not working. My YouTube channel is called "Mostly Functional Engineering" for a reason

## Complete Setup Guide

### Step 1: Connect the Screen to the Pi

The waveshare display is a "hat", so it just plugs directly into the headers of the pi zero. It's pretty straight forward since the display and the pi are basically the same size and shape.

### Step 2: Prepare Your Raspberry Pi

#### Install Raspberry Pi OS
1. **Download Raspberry Pi Imager** from [rpi.org](https://www.raspberrypi.org/software/)
2. **Flash your SD card** with **Raspberry Pi OS Lite** (the lightweight version works perfectly)
3. **Important setup options** in the imager:
   - **Enable SSH** (you'll need this!)
   - **Set username and password** (remember these!)
   - **Configure WiFi** with your network details
   - **Set locale settings** (timezone, keyboard layout)

#### First Boot
1. **Insert the SD card** into your Pi and power it on
2. **Find your Pi's IP address** (check your router's admin page, or use `ping raspberrypi.local`)
3. **Connect via SSH**: `ssh yourusername@your-pi-ip-address`

### Step 3: Update Your System

Run these commands to make sure everything is up to date:

```bash
sudo apt update && sudo apt upgrade -y
```

This might take a few minutes.

### Step 4: Install System Dependencies

We need some system packages for the display and Python libraries:

```bash
sudo apt install -y python3-pip python3-dev python3-numpy python3-pillow git
sudo apt install -y libfreetype6-dev libjpeg-dev libopenjp2-7 libtiff5
```

### Step 5: Enable SPI (Required for E-ink Display)

The E-ink display talks to your Pi through SPI. Enable it:

```bash
sudo raspi-config
```

Navigate to: **Interface Options** → **SPI** → **Yes** → **Finish**

Reboot your Pi: `sudo reboot`

### Step 6: Download This Project

```bash
cd ~
git clone https://github.com/MostlyFunctionalEngineering/EinkDashboard.git
cd EinkDashboard
```

### Step 7: Install Python Dependencies

**Why we use system Python instead of a virtual environment:**
E-ink displays need direct access to your Pi's GPIO pins. Virtual environments can sometimes interfere with this hardware access, so we install everything system-wide to ensure smooth operation. Do this at your own risk, but since this Raspberry Pi Zero will only be used for this display, I'm not worried about interfering with other python processes.

```bash
sudo pip3 install -r requirements.txt
```

This installs all the necessary libraries including:
- **Flask** for the web interface
- **Pillow** for image processing  
- **GPIO libraries** for talking to your display
- **Weather and stock data APIs**
- **And a few other ones that we need for some reason**

*Note: This step takes the longest (5-10 minutes on a Pi Zero). The Pi is downloading and compiling several libraries.*

### Step 8: Configure Your Dashboard

#### Basic Configuration
Edit the configuration file to match your preferences:

```bash
nano config.yaml
```

**Key settings to customize:**
- **Location**: Update the weather location (zip code or city)
- **Stock symbols**: Add your favorite stock tickers
- **Time format**: 12-hour vs 24-hour display
- **Refresh intervals**: How often to update data
- **Timezone**: It should default to the timezone you setup your pi to, but you can change it if desired!

#### **IMPORTANT: Set Up API Keys**

**The YouTube and Stock dashboards will NOT work without API keys!** You need to create a `.env` file with your API credentials.

##### Get a YouTube API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key (keep it secret!)
5. **Optional**: Restrict the API key to only YouTube Data API for security

##### Get Your YouTube Channel ID
1. Go to your YouTube channel
2. Copy the channel ID from the URL:
   - **New format**: `https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxx` (copy the part after `/channel/`)
   - **Custom URL**: If you have a custom URL, go to your channel → About tab → copy the channel ID from there
3. **Alternative method**: Use a tool like [YouTube Channel ID Finder](https://commentpicker.com/youtube-channel-id.php)

##### Get a Finnhub Stock API Key
1. Go to [Finnhub.io](https://finnhub.io/) (free tier available)
2. Sign up for a free account
3. Go to your dashboard and copy your API key
4. Free tier includes 60 API calls per minute (plenty for this project!)

##### Create Your .env File
In your EinkDashboard directory, create a `.env` file:

```bash
nano .env
```

Add your API keys and channel ID like this:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CHANNEL_ID=your_youtube_channel_id_here
FINNHUB_API_KEY=your_finnhub_api_key_here
```

**Example .env file:**
```
YOUTUBE_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
YOUTUBE_CHANNEL_ID=UCPqrW35BnRePrjOEAL8YBVg
FINNHUB_API_KEY=abc123defghijklmnop
```

**IMPORTANT**: 
- Replace the example keys with your actual API keys
- Keep this file secret! Never share it or commit it to version control
- The `.env` file should be in the same directory as `main.py`
- **I AM NOT RESPONSIBLE FOR THIS MAKING TOO MANY API CALLS! PLEASE DOUBLE CHECK THAT YOUR CONFIG SETTINGS DON'T MAKE TOO MANY API CALLS!**

*Note: The clock and weather dashboards work without API keys, so you can test those first!*

### Step 9: Test Your Setup

Let's make sure everything works:

```bash
python3 main.py
```

You should see:
- **Log messages** indicating the dashboard is starting
- **Web server** starting on port 8080
- **Display updates** (if your E-ink display is connected)

**Test the web interface:**
Open your browser and go to: `http://your-pi-ip-address:8080`

You should see a the mega basic control panel that I had AI whip up for me (I'm a mechanical engineer, OK?)

Press `Ctrl+C` to stop the test.

### Step 10: Set Up Auto-Start Service

This makes your dashboard start automatically when your Pi boots up:

```bash
sudo cp eink-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable eink-dashboard.service
sudo systemctl start eink-dashboard.service
```

**Check it's running:**
```bash
sudo systemctl status eink-dashboard.service
```

You should see **"active (running)"** in green!

## Using Your Dashboard

### Web Interface

Open `http://your-pi-ip-address:8080` in any web browser to access the control panel (Your browser might throw a fit or automatically try to go to `https://` which won't work). `8080` is the default port, so you can also just type `http://your-pi-ip-address` and that should work. Regardless of how you get there, you should see: 

#### **Manual Dashboard Selection**
- Choose any dashboard from the dropdown
- Click "Set Dashboard" to switch immediately (well, it takes a second to populate the info, but you get the point)
- Perfect for checking specific information quickly
- NOTE: Manually selecting a dashboard will override auto dashboard cycling!

#### **Auto-Cycling**
- **Enable Auto-Cycling**: Toggle the master switch
- **Set Interval**: Choose how many minutes between switches (1-1440 minutes)
- **Choose Dashboards**: Toggle which dashboards to include in the cycle
- **Save Settings**: Your preferences are saved automatically

#### **Dashboard Options**
- **Clock**: Always-updated time and date
- **Weather**: Local forecast with beautiful weather icons
- **Stocks**: Your portfolio at a glance
- **YouTube**: Channel subscriber count and plot
- **Text**: Simply displays custom text
- **Image**: Simply displays an image (png or bmp only!)

#### **Upload Image**
- **Uploading**: The "image" dashboard can display images at 255x122. It will automatically convert images to gray scale. Uploading an image will automatically set it to the "preferred" image, which will be displayed when the "image" dashboard is selected. 
- **Available Images**: There is a list of available images, which are stored in `assets/User_Images`. Clicking the `X` next to an image will delete it. It is possible to delete an image that is currently the selected image, which may crash the image dashboard.
- **Image Settings**: There are additional image settings (such as fill and fit options) in the advanced configuration
- **Additional Images**: There are some default images and backgrounds in the `assets/Borders_and_Logos` folder 

### Advanced Configuration

#### Raw Config Editing
Click **"Edit Raw Config"** to modify advanced settings:
- Font paths and sizes
- Background images
- Refresh intervals
- API endpoints

There are a TON of settings in here, so feel free to play around with them!

#### Service Management
Useful commands for managing your dashboard:

```bash
# Restart the service
sudo systemctl restart eink-dashboard.service

# View real-time logs
sudo journalctl -u eink-dashboard.service -f

# Stop the service
sudo systemctl stop eink-dashboard.service
```

## Customization

### Adding Your Own Dashboards
The project is designed to be extensible! Check the `dashboards/` folder to see how existing dashboards work, then create your own.

### Custom Fonts
Drop new fonts into the `fonts/` folder and reference them in `config.yaml`. NOTE: I only really tested stuff using one font. You might have to play with the config or locations of things if you start picking other fonts!!! Things like locations and sizing will likely absolutely blow up if you start messing with things too much lol

### Background Images
Add custom backgrounds to `assets/` and configure them per dashboard.

### Weather Icons
The `assets/Weather_Icons/` folder contains some basic free weather icons that I snagged online, feel free to use your own. 

## Troubleshooting

### Dashboard Not Updating?
```bash
# Check service status
sudo systemctl status eink-dashboard.service

# Check logs for errors
sudo journalctl -u eink-dashboard.service --no-pager
```

### Web Interface Not Loading?
- Verify your Pi's IP address: `hostname -I`
- Check if port 8080 is accessible: `sudo netstat -tlnp | grep 8080`
- Try restarting: `sudo systemctl restart eink-dashboard.service`

### Display Issues?
- Verify SPI is enabled: `ls /dev/spi*` (should show `/dev/spidev0.0` and `/dev/spidev0.1`)
- Check display wiring matches your model
- Look for errors in the logs

### Permission Problems?
```bash
# Make sure you own the project directory
sudo chown -R $USER:$USER ~/EinkDashboard

# Verify service file permissions
sudo chmod 644 /etc/systemd/system/eink-dashboard.service
```

## Some Tips

1. **Bookmark the web interface** on your phone for quick dashboard switching
2. **Set different intervals** for different scenarios (5 minutes for general use, 30 seconds for demos)
3. **Use the clock dashboard** as your "default" since it updates every minute
4. **Check the logs** if something seems off - they're very helpful for debugging
5. **Experiment with fonts and backgrounds** - the visual customization is endless!

## Contributing

Found a bug? I don't care! (JK, I'm sure it's riddled with them) I made this so people can use it and do whatever they want with it. Feel free to: 

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source! Feel free to use it, modify it, and share it!

## Acknowledgments

- Free use weather icons from [I found these here](https://www.dovora.com/resources/weather-icons/) - check License.txt in assets/Weather_Icons/
- Free use font collections from various creators (see [fontspace.com](https://www.fontspace.com))

---

**Enjoy your new E-ink dashboard! **

*If you found this helpful, consider starring the repository to help others find it, and please consider subscribing to my YouTube channel for more fun projects!*