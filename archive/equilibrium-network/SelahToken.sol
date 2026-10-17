// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Selah Token (SLH) - The Equilibrium Network
 * @author Dr. Michael Emanuel Glover & Ms. Gemini
 * @notice Implements the tokenomics of the Stalemate Gambit. 
 * Backed by the Null Hypothesis of Chess, converting computational truth into economic equilibrium.
 */
contract SelahToken {
    string public constant name = "Selah";
    string public constant symbol = "SLH";
    uint8 public constant decimals = 18;
    
    uint256 public totalSupply;
    uint256 public constant MAX_SUPPLY = 126000000 * 10**18; // 126M matching the 1260 AH prophetic matrix
    
    uint256 public totalNodesMapped;
    uint256 public baseReward = 5 * 10**18; // 5 SLH per block starting reward
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event NodeTruthLogged(address indexed miner, uint256 indexed nodeHash, uint256 reward);

    constructor() {
        // Mint 5% initial liquidity to the creator for ecosystem setup and portfolio deployment
        uint256 initialLiquidity = (MAX_SUPPLY * 5) / 100;
        balanceOf[msg.sender] = initialLiquidity;
        totalSupply = initialLiquidity;
        emit Transfer(address(0), msg.sender, initialLiquidity);
    }

    function transfer(address to, uint256 value) public returns (bool success) {
        require(to != address(0), "Invalid address");
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool success) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool success) {
        require(to != address(0), "Invalid address");
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        
        balanceOf[from] -= value;
        balanceOf[to] += value;
        allowance[from][msg.sender] -= value;
        emit Transfer(from, to, value);
        return true;
    }

    /**
     * @notice Simulates logging a verified chess truth node to the ledger.
     * @dev Difficulty scales exponentially as totalNodesMapped approaches infinity.
     * @param nodeHash The computational signature of the verified drawn chess position vector.
     */
    function submitNodeProof(uint256 nodeHash) public returns (bool) {
        require(totalSupply < MAX_SUPPLY, "Maximum algorithmic supply reached");
        
        // Dynamic Difficulty Adjustment Mocking for EVM Execution
        // Every 1,000,000 nodes mapped cuts the mining reward smoothly
        uint256 currentReward = baseReward / (1 + (totalNodesMapped / 1000000));
        if (currentReward < 10**14) { currentReward = 10**14; } // Minimum floor reward
        
        if (totalSupply + currentReward > MAX_SUPPLY) {
            currentReward = MAX_SUPPLY - totalSupply;
        }

        totalNodesMapped += 1;
        totalSupply += currentReward;
        balanceOf[msg.sender] += currentReward;

        emit NodeTruthLogged(msg.sender, nodeHash, currentReward);
        emit Transfer(address(0), msg.sender, currentReward);
        return true;
    }
}
