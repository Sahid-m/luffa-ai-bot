import {useEffect, useState} from 'react';
import './styles.css';

import {
    EndlessLuffaSdk,
    UserResponseStatus,
    EndLessSDKEvent,
} from '@luffalab/luffa-endless-sdk';

import {
    Network,
    TypeTagU64,
    EndlessConfig,
    Endless,
    TypeTagU8
} from '@endlesslab/endless-ts-sdk';

const jssdk = new EndlessLuffaSdk({
    // mainnet or testnet
    network: 'testnet',
    miniprogram: false,
});

const config = new EndlessConfig({
    network: Network.TESTNET
});
const endless = new Endless(config);

const connectWalletHandler = async () => {
    const connectRes = await jssdk.connect();
    if (connectRes.status === UserResponseStatus.APPROVED) {
        return connectRes;
    }
    return null;
};

// const disconnectWalletHandler = () => {
//   jssdk.disconnect().then(() => {
//     console.log('disconnect success');
//   })
// };
//
// const getAccountHandler = async () => {
//     const getAccountRes = await jssdk.getAccount();
//
//     if (getAccountRes.status === UserResponseStatus.APPROVED) {
//         console.log('getAccountRes =====>', getAccountRes);
//     }
// };

const disconnectHandler = () => {
    console.log('disconnect');
};

jssdk.on(EndLessSDKEvent.DISCONNECT, disconnectHandler);

jssdk.off(EndLessSDKEvent.DISCONNECT, disconnectHandler);

// Demo React component for interacting with a blockchain-based number guessing game using Luffa Wallet.
// Includes wallet connection, game creation, game discovery, and guess submission.
function Home() {
    const [accountAddress, setAccountAddress] = useState("");
    const [games, setGames] = useState([]);
    const [selectedGameId, setSelectedGameId] = useState(null);
    const [guess, setGuess] = useState(10);
    const [result, setResult] = useState("");
    const [targetNumber, setTargetNumber] = useState("");

    // Automatically connects wallet on load and listens for account changes.
    useEffect(() => {
        connectWalletHandler().then(r => {
            console.log(r);
        });

        jssdk.on(EndLessSDKEvent.CONNECT, (res) => {
            setAccountAddress(res.address);
        });

        jssdk.on(EndLessSDKEvent.ACCOUNT_CHANGE, (res) => {
            setAccountAddress(res.address);
        });

    }, [])

    const package_address = "a71ad019c19b607a1829f2811672d97fd956cdfb4d7c78221d7e299bfd823aab";

    // Calls the Move smart contract to start a new game with a hidden number.
    const start_game = async () => {
        const transactionData = {
            payload: {
                function: `${package_address}::main::start_game`,
                functionArguments: ["100"],
                abi: {
                    typeParameters: [],
                    parameters: [new TypeTagU64()],
                },
            },
        };

        const transactionRes = await jssdk.signAndSubmitTransaction(transactionData);

        if (transactionRes.status === UserResponseStatus.APPROVED) {
            await endless.waitForTransaction({
                transactionHash: transactionRes.args.hash,
            });
            await find_games();
        }
    }

    // Submits a guess to the smart contract and updates the result based on event logs.
    const submit_guess = async () => {
        if (!accountAddress) {
            console.log('accountAddress is empty');
            return;
        }

        const transactionData = {
            payload: {
                function: `${package_address}::main::submit_guess`,
                functionArguments: [selectedGameId, guess],
                abi: {
                    typeParameters: [],
                    parameters: [new TypeTagU64(), new TypeTagU8()],
                },
            },
        }

        const transactionRes = await jssdk.signAndSubmitTransaction(transactionData);
        if (transactionRes.status === UserResponseStatus.APPROVED) {
            const transaction = await endless.waitForTransaction({
                transactionHash: transactionRes.args.hash,
            });

            console.log("submit_guess", transaction);

            await find_games();
            const {events} = transaction;
            for (const event of events) {
                const {type, data} = event;
                if (/main::GameWinner/.test(type)) {
                    const {winner, hidden_number} = data;
                    setTargetNumber(hidden_number);
                    if (winner === accountAddress) {
                        setResult("You Won");
                    } else {
                        setResult("You Lost");
                    }
                }
            }
        }
    }

    // Queries active games from the blockchain.
    const find_games = async () => {
        const config = new EndlessConfig({
            network: Network.TESTNET
        });
        const endless = new Endless(config);
        if (!accountAddress) {
            console.log('accountAddress is empty');
            return;
        }

        const data = await endless.view({
            payload: {
                function: `${package_address}::main::get_active_game_ids`,
                typeArguments: [],
                functionArguments: [],
            }
        });
        if (data.length > 0) {
            setGames(data[0]);
        }
    }

    return (
        <div className="container">
            <div className="connected-address">
                <span>🔗 Connected: </span>{accountAddress}
            </div>
            <button
                className="button"
                onClick={() => start_game()}
            >
                Start Game
            </button>
            <button
                className="button"
                onClick={() => find_games()}
            >
                Find Games
            </button>

            <div className="game-list">
                <p>Active Games:</p>

                <ul className="no-bullets">
                    {games.map((game, index) => (

                        <li
                            key={index}
                            className={game === selectedGameId ? "game-item selected" : "game-item"}
                            onClick={() => setSelectedGameId(game)}
                        >
                            Game ID: {game}
                        </li>
                    ))}
                </ul>
            </div>

            <input
                type="number"
                min={1}
                max={100}
                value={guess}
                onChange={(e) => setGuess(e.target.value)}
                className="input"
            />
            <button
                className="button"
                onClick={() => submit_guess()}
            >
                Submit Guess
            </button>
            {result !== "" && (
                <div
                    className={result === "You Won" ? "result-box win" : result === "You Lost" ? "result-box lose" : "result-box"}>
                    <p style={{margin: 0, fontWeight: "bold"}}>
                        {result === "You Won" && "🎉 You Won!"}
                        {result === "You Lost" && "😞 You Lost"}
                        {result === "" && "🎯 No Result Yet"}
                    </p>
                    <p style={{margin: "6px 0 0"}}>🎲 Your Guess: {guess}</p>
                    <p style={{margin: "4px 0 0"}}>🔢 Target Number: {targetNumber}</p>
                </div>
            )}

        </div>
    )
}

export default Home;
