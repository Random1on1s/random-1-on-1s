const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { fs } = require('fs');
const { process } = require('process');

const commands =  fs.readdirSync('./commands')
    .filter(file => file.endsWith('.js'))
    .map(file => require(`./commands/${file}`).data.toJSON());

const rest = new REST({ version: '9' }).setToken(process.env.BOT_TOKEN);

rest.put(Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID), { body: commands })
    .then(() => console.log('Registered commands for Random 1-on-1 bot.'))
    .catch(console.error);
