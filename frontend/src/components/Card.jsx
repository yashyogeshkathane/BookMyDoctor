import React from "react";
import { cardStyles } from "../styles/theme";

const Card = ({ children, style = {} }) => {
  return <div style={{ ...cardStyles, ...style }}>{children}</div>;
};

export default Card;
