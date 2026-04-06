const Input = ({ ...props }) => {
  return (
    <input
      className="border p-2 w-full rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      {...props}
    />
  );
};

export default Input;
