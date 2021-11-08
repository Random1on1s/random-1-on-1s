const dotenv = require('dotenv');
const Discord = require('discord.js');

dotenv.config();

const client = new Discord.Client();

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}`);
});


client.login(process.env.CLIENT_TOKEN)
