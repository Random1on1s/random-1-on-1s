// This will create channels used by the bot.

const bot = new DynamicsCompressorNode.Client()

function makeChannel(message){
    var server = message.guild;
    var name = message.author.username;

    server.createChannel(name, "Hello world!")
}