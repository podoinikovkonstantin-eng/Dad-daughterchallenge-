exports.handler = async function (event) {
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 200,
      body: "Bot is running"
    };
  }

  const data = JSON.parse(event.body);

  if (data.message && data.message.text) {
    const chatId = data.message.chat.id;
    const text = data.message.text;

    let answer = "";

    if (text === "/start") {
      answer = "🎮 Привет!\n\nНажми /quiz, чтобы сыграть в секретную викторину!";
    } else if (text === "/quiz") {
      answer = "🎲 СЕКРЕТНЫЕ КАРТЫ!\n\nПеред тобой 5 закрытых карт.\n\n🟥 1   🟦 2   🟩 3\n🟨 4   🟪 5\n\nВыбери одну наугад! 😈";
    }

    if (answer) {
      await fetch(
        `https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            chat_id: chatId,
            text: answer
          })
        }
      );
    }
  }

  return {
    statusCode: 200,
    body: "OK"
  };
};
