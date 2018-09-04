pragma solidity ^0.4.7;
import "remix_tests.sol"; // this import is automatically injected by Remix.
import "./ballot.sol";

contract aagcoin_ico {
   
    uint public max_aagcoins = 1000000;
   
    uint public usd_to_aagcoins = 1000;
    
    uint public total_aagcoins_bought = 0;
    
    mapping(address => uint) equity_aagcoins;
    mapping(address => uint) equity_usd;

    modifier can_buy_aagcoins(uint usd_invested) {
        require (usd_invested * usd_to_aagcoins + total_aagcoins_bought <= max_aagcoins);
        _;
    }
    
    function equity_in_aagcoins(address investor) external constant returns(uint) {
        return equity_aagcoins[investor];
    }
    
    function equity_in_usd(address investor) external constant returns(uint) {
        return equity_usd[investor];
    }
 
    function buy_aagcoins(address investor, uint usd_invested) external
    can_buy_aagcoins(usd_invested) {
        uint aagcoins_bought = usd_invested * usd_to_aagcoins;
        equity_aagcoins[investor] += aagcoins_bought;
        equity_usd[investor] = equity_aagcoins[investor] / 1000;
        total_aagcoins_bought += aagcoins_bought;
    }
    
    function sell_aagcoins(address investor, uint aagcoins_sold) external {
        equity_aagcoins[investor] -= aagcoins_sold;
        equity_usd[investor] = equity_aagcoins[investor] / 1000;
        total_aagcoins_bought -= aagcoins_sold;
    }
}
